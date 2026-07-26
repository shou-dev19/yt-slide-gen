/**
 * レンダリング済みの DOM から「いらすとや主役化」と「テキストの見切れ・はみ出し」を計測する。
 *
 * 背景:
 *   generate-html-slides の SKILL.md は §7「イラストが見出しより大きい・目立つ構図は不合格」
 *   §9「片ページ丸ごと汎用イラストだけの構成は禁止」§10「オーバーフロー厳禁」と規定しているが、
 *   これらは agy の目視レビュー（Step 4.5）とオーケストレーターのセルフチェック頼みだった。
 *   目視は当たり外れがあり、特に「テキストの見切れ」は PNG を見ても気づきにくい（末尾が
 *   きれいに切れていると、そういうデザインに見えてしまう）。どちらも DOM からは確定的に
 *   測れるので、余白計測（measure_whitespace.js）と同じくキャプチャ時に機械判定する。
 *
 * 測り方:
 *   - **いらすとや主役化**: ページの内容領域に対する、いらすとや画像（`/irasutoya/` 配下）の
 *     占有面積比と、テキスト要素の占有面積比を矩形の和で求める。加えて、ページ内で最大の
 *     font-size を持つテキスト要素を「見出し」とみなし、イラスト面積との比を出す。
 *     面積の和は座標圧縮による厳密な矩形和集合で、入れ子要素の二重計上を避ける。
 *   - **見切れ（clipped）**: `overflow` が visible 以外の要素で `scrollWidth/Height` が
 *     `clientWidth/Height` を超えるもの。実際にブラウザが内容を切り落としている状態そのもの。
 *     入れ子で親子とも該当する場合は、原因に近い最内側の要素だけを残す。
 *   - **はみ出し（outOfBounds）**: 内容領域の外へ出ている要素。`.page` の padding-bottom は
 *     字幕帯用に空けた紙面（SKILL.md §10「本の下端より下は字幕帯」）なので、ここへ本文が
 *     侵入していれば検出される。
 */

/** ブラウザ内で実行される計測関数の本体（page.evaluate に渡す）。 */
const measureInPage = (slideSelector, index, opts) => {
    const { excludeSelectors, illustrationSrcPattern, tolerancePx, boundsTolerancePx } = opts;
    const slide = document.querySelectorAll(slideSelector)[index];
    if (!slide) return null;

    const isExcluded = (el) => excludeSelectors.some((sel) => el.closest(sel));

    const hasDirectText = (el) =>
        Array.from(el.childNodes).some(
            (n) => n.nodeType === 3 && n.nodeValue.trim().length > 0,
        );

    /** 要素を人が読める短いパスにする（修正時に該当箇所を特定するため）。 */
    const describe = (el) => {
        const parts = [];
        let cur = el;
        for (let i = 0; i < 3 && cur && cur !== document.body; i++) {
            const cls = Array.from(cur.classList).slice(0, 2).join('.');
            parts.unshift(cls ? `${cur.tagName.toLowerCase()}.${cls}` : cur.tagName.toLowerCase());
            cur = cur.parentElement;
        }
        return parts.join(' > ');
    };

    const snippet = (el) => {
        const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
        return t.length > 40 ? `${t.slice(0, 40)}…` : t;
    };

    /** 矩形集合の和集合の面積（座標圧縮。入れ子・重なりを二重に数えない）。 */
    const unionArea = (rects) => {
        if (rects.length === 0) return 0;
        const xs = Array.from(new Set(rects.flatMap((r) => [r.left, r.right]))).sort((a, b) => a - b);
        let total = 0;
        for (let i = 0; i < xs.length - 1; i++) {
            const x0 = xs[i];
            const x1 = xs[i + 1];
            const w = x1 - x0;
            if (w <= 0) continue;
            const intervals = rects
                .filter((r) => r.left <= x0 && r.right >= x1)
                .map((r) => [r.top, r.bottom])
                .sort((a, b) => a[0] - b[0]);
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
            total += w * covered;
        }
        return total;
    };

    /** ページの内容領域（padding を除いた box）。余白計測と同じ定義。 */
    const contentBox = (pageEl) => {
        const style = getComputedStyle(pageEl);
        const rect = pageEl.getBoundingClientRect();
        const left = rect.left + (parseFloat(style.paddingLeft) || 0);
        const right = rect.right - (parseFloat(style.paddingRight) || 0);
        const top = rect.top + (parseFloat(style.paddingTop) || 0);
        const bottom = rect.bottom - (parseFloat(style.paddingBottom) || 0);
        return { left, right, top, bottom, width: right - left, height: bottom - top };
    };

    const clipToBox = (r, box) => {
        const left = Math.max(r.left, box.left);
        const right = Math.min(r.right, box.right);
        const top = Math.max(r.top, box.top);
        const bottom = Math.min(r.bottom, box.bottom);
        if (right - left <= 0 || bottom - top <= 0) return null;
        return { left, right, top, bottom };
    };

    /**
     * はみ出し判定に使う枠。
     *   - 見開きの `.page`: **内容領域**（padding を除く）。下部 padding は字幕帯用に空けた紙面で、
     *     ここへ本文が入ること自体が SKILL.md §10 違反なので検出したい。
     *   - std / ショート: **要素の外形**（padding を含む）。これらの書式は `.watermark` や
     *     `.slide-illust` のような装飾を padding 領域へ意図的に絶対配置するため、内容領域で
     *     測ると全スライドが誤検出になる（ショートの実デッキで13件の誤検出を確認）。
     *     この書式で問題になるのは、キャンバス自体からの逸脱（overflow:hidden で消える）だけ。
     */
    const boundsBox = (pageEl, isPage) => {
        if (isPage) return contentBox(pageEl);
        const r = pageEl.getBoundingClientRect();
        return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height };
    };

    const measurePage = (pageEl, label, isPage) => {
        const box = contentBox(pageEl);
        if (box.width <= 0 || box.height <= 0) return null;
        const boxArea = box.width * box.height;
        const bounds = boundsBox(pageEl, isPage);

        const illustrationRects = [];
        const illustrationImages = [];
        const textRects = [];
        let headline = null;
        const clippedCandidates = []; // { el, entry } — 最内側の絞り込みに要素の包含関係を使う
        const outOfBounds = [];

        const elements = [pageEl, ...pageEl.querySelectorAll('*')];
        for (const el of elements) {
            if (el !== pageEl && isExcluded(el)) continue;

            // --- 見切れ（ブラウザが実際に内容を切っている） ---
            const style = getComputedStyle(el);
            const overX = style.overflowX !== 'visible';
            const overY = style.overflowY !== 'visible';
            const clipX = overX ? el.scrollWidth - el.clientWidth : 0;
            const clipY = overY ? el.scrollHeight - el.clientHeight : 0;
            // 「自分のテキスト」を切っている要素だけを見切れとして報告する。子孫のテキストまで
            // 対象にすると、角の菱形アクセントのように**意図的に枠外へ抜く装飾**を持つ
            // コンテナ（.slide-container など）が毎回引っかかる（実測で確認済み）。
            // 子要素が枠外へ押し出されるタイプの溢れは outOfBounds 側が拾う。
            if ((clipX > tolerancePx || clipY > tolerancePx) && hasDirectText(el)) {
                clippedCandidates.push({
                    el,
                    entry: {
                        label,
                        path: describe(el),
                        text: snippet(el),
                        clippedXPx: Math.round(clipX),
                        clippedYPx: Math.round(clipY),
                    },
                });
            }

            if (el === pageEl) continue;

            const rect = el.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) continue;

            const isImg = el.tagName.toLowerCase() === 'img';
            const isText = hasDirectText(el);

            // --- 枠からのはみ出し（見開きでは字幕帯への侵入を含む。枠の定義は boundsBox 参照） ---
            if (isImg || isText) {
                const out = {
                    top: Math.round(bounds.top - rect.top),
                    bottom: Math.round(rect.bottom - bounds.bottom),
                    left: Math.round(bounds.left - rect.left),
                    right: Math.round(rect.right - bounds.right),
                };
                const worst = Math.max(out.top, out.bottom, out.left, out.right);
                if (worst > boundsTolerancePx) {
                    outOfBounds.push({
                        label,
                        path: describe(el),
                        text: isImg ? (el.getAttribute('src') || '').split('/').pop() : snippet(el),
                        overflowPx: Object.fromEntries(
                            Object.entries(out).filter(([, v]) => v > boundsTolerancePx),
                        ),
                    });
                }
            }

            const clippedRect = clipToBox(rect, box);
            if (!clippedRect) continue;

            if (isImg && (el.getAttribute('src') || '').includes(illustrationSrcPattern)) {
                illustrationRects.push(clippedRect);
                illustrationImages.push({
                    src: (el.getAttribute('src') || '').split('/').pop(),
                    widthRatio: Number(((clippedRect.right - clippedRect.left) / box.width).toFixed(3)),
                    heightPx: Math.round(clippedRect.bottom - clippedRect.top),
                });
            } else if (isText) {
                textRects.push(clippedRect);
                const fontSize = parseFloat(style.fontSize) || 0;
                if (!headline || fontSize > headline.fontSize) {
                    headline = {
                        fontSize: Math.round(fontSize),
                        text: snippet(el),
                        area:
                            (clippedRect.right - clippedRect.left) *
                            (clippedRect.bottom - clippedRect.top),
                    };
                }
            }
        }

        const illustrationArea = unionArea(illustrationRects);
        const textArea = unionArea(textRects);

        // 親子ともに見切れている場合は、原因に近い最内側の要素だけを残す
        // （`.page` が溢れている報告より、溢れさせている `.rows` の報告のほうが直しやすい）。
        const clipped = clippedCandidates
            .filter((c) => !clippedCandidates.some((o) => o.el !== c.el && c.el.contains(o.el)))
            .map((c) => c.entry);

        return {
            page: {
                label,
                illustrationCount: illustrationImages.length,
                illustrationImages,
                illustrationAreaRatio: Number((illustrationArea / boxArea).toFixed(3)),
                textAreaRatio: Number((textArea / boxArea).toFixed(3)),
                headlineFontSize: headline ? headline.fontSize : null,
                headlineText: headline ? headline.text : null,
                // 参考値（判定には使わない。理由は findIllustrationDominant のコメント）。
                illustrationVsHeadline:
                    headline && headline.area > 0 && illustrationArea > 0
                        ? Number((illustrationArea / headline.area).toFixed(2))
                        : null,
            },
            clipped,
            outOfBounds,
        };
    };

    const pageEls = slide.querySelectorAll('.page');
    const targets =
        pageEls.length > 0
            ? Array.from(pageEls).map((p, i) => [
                p,
                p.classList.contains('left') ? 'left' : p.classList.contains('right') ? 'right' : `page${i + 1}`,
            ])
            // 見開きでない std スライド（冒頭の導入カット）はコンテナ自体を1ページとして測る。
            : [[slide, 'std']];

    const pages = [];
    let clipped = [];
    let outOfBounds = [];
    for (const [el, label] of targets) {
        const result = measurePage(el, label, pageEls.length > 0);
        if (!result) continue;
        pages.push(result.page);
        clipped = clipped.concat(result.clipped);
        outOfBounds = outOfBounds.concat(result.outOfBounds);
    }

    return { pages, clipped, outOfBounds, isSpread: pageEls.length > 0 };
};

/**
 * 内容ではない装飾クロム。ノンブル・図鑑インデックスタブ（long）に加え、ショートの
 * `.watermark`（`top:-40px` / `opacity:0.07` の巨大な番号。枠外へ抜けるのが意図）も除く。
 */
export const DEFAULT_EXCLUDE_SELECTORS = ['.page-no', '.index-tab', '.watermark'];

export const DEFAULT_LAYOUT_OPTIONS = {
    excludeSelectors: DEFAULT_EXCLUDE_SELECTORS,
    /** いらすとや画像の判別。SKILL.md §9 の「汎用イラスト」は public/images/irasutoya/ 配下。 */
    illustrationSrcPattern: '/irasutoya/',
    /** 見切れ判定の許容値。サブピクセル・行の高さの丸めによる誤検出を避ける。 */
    tolerancePx: 2,
    /**
     * はみ出し判定の許容値。`.visual img` のように `height:100%` ＋ `max-height` で内容領域に
     * ぴったり収める画像は、丸めで十数 px だけ食み出すことがある（実測で 11px の例を確認）。
     * 字幕帯は約250px あるので、この程度は視覚的な問題にならない。実際の違反は
     * 100px 単位で出る（検証用の壊れたスライドでは 190px / 218px）ので、取りこぼしはない。
     */
    boundsTolerancePx: 12,
};

/**
 * 1スライドのレイアウトを計測する。
 * @returns {Promise<{pages:object[], clipped:object[], outOfBounds:object[], isSpread:boolean}>}
 */
export async function measureSlideLayout(page, slideSelector, index, options = DEFAULT_LAYOUT_OPTIONS) {
    const merged = { ...DEFAULT_LAYOUT_OPTIONS, ...options };
    return (
        (await page.evaluate(measureInPage, slideSelector, index, merged)) || {
            pages: [],
            clipped: [],
            outOfBounds: [],
            isSpread: false,
        }
    );
}

/**
 * いらすとや画像がページの主役になっているページを抽出する。
 *
 * 対応する規則: §7「主役はフックとなるテキスト。いらすとやは脇役。イラストが見出しより
 * 大きい・目立つ構図は不合格」／§9「片ページ丸ごと汎用イラストだけの構成は禁止。イラストが
 * ページの大半を占めるのは不合格」。
 *
 * 判定に使うのは次の2つで、どちらも「ページ内容に占める面積」で測る:
 *   1. `illustrationAreaRatio >= areaRatio` … ページの大半がイラスト（§9）。
 *   2. `illustrationAreaRatio > textAreaRatio` … テキストよりイラストが大きい＝主役化（§7）。
 *
 * **「見出し要素の矩形との比」（illustrationVsHeadline）は判定に使わない。** いらすとやの PNG は
 * 四辺に透明の余白を持つため bbox 面積が実際の絵より大きく出る一方、見出しの bbox は文字に
 * ぴったり付く。この比で判定すると、目視で明らかにテキストが主役の導入スライドが 1.06〜1.67 を
 * 示して軒並み不合格になった（下記の校正データ）。参考値としてレポートには残す。
 *
 * 校正（2026-07-26・38本目のデッキ 40枚 / 77ページ。評価ループを通過済み＝全ページ合格が正解）:
 *   いらすとやを含む3ページの実測は
 *     std   スライド1: illust 0.129 / text 0.442（見出し比 1.06）
 *     std   スライド2: illust 0.129 / text 0.398（見出し比 1.67）
 *     spread 6-2 right: illust 0.099 / text 0.413（見出し比 0.69）
 *   いずれも面積比では text が illust の 3〜4 倍あり、閾値 0.4 とテキスト比較の双方で余裕を持って
 *   合格する。
 *
 * @param {{id:string, pages:object[]}[]} results
 */
export function findIllustrationDominant(results, { areaRatio = 0.4 } = {}) {
    const over = [];
    for (const { id, pages } of results) {
        for (const p of pages) {
            if (p.illustrationCount === 0) continue;
            const reasons = [];
            if (p.illustrationAreaRatio >= areaRatio) reasons.push('ページの大半がイラスト');
            if (p.illustrationAreaRatio > p.textAreaRatio) reasons.push('テキストよりイラストが大きい');
            if (reasons.length === 0) continue;
            over.push({
                id,
                label: p.label,
                reasons,
                illustrationAreaRatio: p.illustrationAreaRatio,
                textAreaRatio: p.textAreaRatio,
                images: p.illustrationImages.map((i) => i.src),
            });
        }
    }
    return over;
}

/**
 * 見切れ・はみ出しをスライド横断で集計する。
 * @param {{id:string, clipped:object[], outOfBounds:object[]}[]} results
 */
export function collectOverflow(results) {
    const clipped = [];
    const outOfBounds = [];
    for (const r of results) {
        for (const c of r.clipped) clipped.push({ id: r.id, ...c });
        for (const o of r.outOfBounds) outOfBounds.push({ id: r.id, ...o });
    }
    return { clipped, outOfBounds };
}
