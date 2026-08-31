/**
 * 見開きスライドの「余白率」をレンダリング済みの DOM から計測する。
 *
 * 背景:
 *   generate-html-slides の SKILL.md §10 は「ページの1/3以上が空白なら不合格」と数値で
 *   規定しているが、これまでは agy の目視レビュー（Step 4.5）と人間の目視だけで判定していた。
 *   agy は当たり外れがあり、実在しないルールを引用することもある一方で、この規則自体は
 *   機械的に測れる。2026-07-26 のランでは12枚が同じ理由で不合格になり、評価ラウンドを
 *   1周余計に回している。計測で先に潰せば、agy には余白以外（誤字・トンマナ・画像の
 *   適切さ）に専念させられる。
 *
 * 測り方:
 *   ページの内容領域（.page の padding を除いた box。下部 padding は字幕帯用の意図的な余白
 *   なので最初から内容領域に含めない）に対して、実際に「描画されている要素」が縦方向に
 *   占める区間の和집合を求め、`1 - 占有高 / 内容領域高` を余白率とする。
 *   区間の和集合を使うので、下端の空きだけでなく中間の大きな空きも拾える。
 *
 *   「描画されている要素」= 直接の子に非空白テキストを持つ要素 / img・svg・canvas /
 *   背景色や枠線が視認できる要素（カード・バッジ）。図鑑インデックスタブなどの
 *   装飾クロムは内容ではないので除外する。
 */

/** ブラウザ内で実行される計測関数の本体（page.evaluate に渡す）。 */
const measureInPage = (slideSelector, index, excludeSelectors) => {
    const slide = document.querySelectorAll(slideSelector)[index];
    if (!slide) return null;

    const isExcluded = (el) => excludeSelectors.some((sel) => el.closest(sel));

    const hasDirectText = (el) =>
        Array.from(el.childNodes).some(
            (n) => n.nodeType === 3 && n.nodeValue.trim().length > 0,
        );

    const isPainted = (el) => {
        const tag = el.tagName.toLowerCase();
        if (tag === 'img' || tag === 'svg' || tag === 'canvas' || tag === 'video') return true;
        if (hasDirectText(el)) return true;
        const style = getComputedStyle(el);
        const bg = style.backgroundColor || '';
        const alphaMatch = bg.match(/rgba?\([^)]*?,\s*([\d.]+)\s*\)$/);
        const bgAlpha = alphaMatch ? parseFloat(alphaMatch[1]) : bg.startsWith('rgb(') ? 1 : 0;
        if (bgAlpha > 0.02) return true;
        if (style.backgroundImage && style.backgroundImage !== 'none') return true;
        const bw = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
        if (bw > 0 && style.borderTopStyle !== 'none') return true;
        return false;
    };

    /** 1つの「ページ」（見開きなら左右それぞれ、std なら全体）の余白率を測る。 */
    const measurePage = (pageEl, label) => {
        const style = getComputedStyle(pageEl);
        const rect = pageEl.getBoundingClientRect();
        const padTop = parseFloat(style.paddingTop) || 0;
        const padBottom = parseFloat(style.paddingBottom) || 0;
        const areaTop = rect.top + padTop;
        const areaBottom = rect.bottom - padBottom;
        const areaHeight = areaBottom - areaTop;
        if (areaHeight <= 0) return null;

        const intervals = [];
        for (const el of pageEl.querySelectorAll('*')) {
            if (el === pageEl || isExcluded(el)) continue;
            if (!isPainted(el)) continue;
            const r = el.getBoundingClientRect();
            if (r.height <= 0 || r.width <= 0) continue;
            const top = Math.max(r.top, areaTop);
            const bottom = Math.min(r.bottom, areaBottom);
            if (bottom - top <= 0) continue;
            intervals.push([top, bottom]);
        }

        intervals.sort((a, b) => a[0] - b[0]);
        let covered = 0;
        let curStart = null;
        let curEnd = null;
        for (const [s, e] of intervals) {
            if (curStart === null) {
                curStart = s;
                curEnd = e;
            } else if (s <= curEnd) {
                curEnd = Math.max(curEnd, e);
            } else {
                covered += curEnd - curStart;
                curStart = s;
                curEnd = e;
            }
        }
        if (curStart !== null) covered += curEnd - curStart;

        // 内容の最下端から内容領域の下端までの空き（＝いちばん目につく「下がスカスカ」）も併記する。
        const contentBottom = intervals.length > 0 ? Math.max(...intervals.map((i) => i[1])) : areaTop;
        return {
            label,
            areaHeight: Math.round(areaHeight),
            coveredHeight: Math.round(covered),
            whitespaceRatio: Number((1 - covered / areaHeight).toFixed(3)),
            bottomGapRatio: Number(((areaBottom - contentBottom) / areaHeight).toFixed(3)),
        };
    };

    const pages = slide.querySelectorAll('.page');
    if (pages.length > 0) {
        return Array.from(pages)
            .map((p, i) => measurePage(p, p.classList.contains('left') ? 'left' : p.classList.contains('right') ? 'right' : `page${i + 1}`))
            .filter(Boolean);
    }
    // 見開きでない std スライド（冒頭の導入カット）はコンテナ自体を1ページとして測る。
    const single = measurePage(slide, 'std');
    return single ? [single] : [];
};

/** 図鑑インデックスタブなど、内容ではない装飾クロム。 */
export const DEFAULT_EXCLUDE_SELECTORS = ['.index-tab'];

/**
 * 1スライドの余白を計測する。
 * @returns {Promise<{label:string, whitespaceRatio:number, bottomGapRatio:number}[]>}
 */
export async function measureSlideWhitespace(page, slideSelector, index, excludeSelectors = DEFAULT_EXCLUDE_SELECTORS) {
    return (await page.evaluate(measureInPage, slideSelector, index, excludeSelectors)) || [];
}

/**
 * 計測結果から閾値超過のページを抽出する。
 *
 * 判定に使うのは **bottomGapRatio（内容の最下端から内容領域の下端までの空き）** で、
 * whitespaceRatio（占有区間の和集合から出す総余白率）は参考値として返すだけにする。
 * 総余白率で判定すると、章扉や CTA のように大きなアイコン1つを縦中央に置く
 * 意図的なレイアウトが軒並み引っかかる（上下に均等な余白が空くため）。
 * 一方、実際に運営者と評価エージェントの双方が「スカスカ」と指摘してきた不具合は
 * 「内容が上半分に固まって下が大きく空く」形であり、これは下端の空きで素直に測れる。
 *
 * 校正（2026-07-26・38本目のデッキ 40枚 / 77ページ）:
 *   目視で許容と判断した状態での bottomGapRatio の最大は 0.29（章扉の右ページ）。
 *   修正前に12枚が指摘された状態では 0.35〜0.40 程度だった。閾値 1/3 はこの間に入る。
 *
 * @param {{id:string, pages:{label:string, whitespaceRatio:number, bottomGapRatio:number}[]}[]} results
 * @param {number} threshold 下端の空きの上限（既定 1/3。SKILL.md §10 の「1/3以上が空白なら不合格」）
 */
export function findOverThreshold(results, threshold = 1 / 3) {
    const over = [];
    for (const { id, pages } of results) {
        for (const p of pages) {
            if (p.bottomGapRatio >= threshold) {
                over.push({ id, label: p.label, whitespaceRatio: p.whitespaceRatio, bottomGapRatio: p.bottomGapRatio });
            }
        }
    }
    return over;
}
