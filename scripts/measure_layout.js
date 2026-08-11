/**
 * レンダリング済みの DOM から「いらすとや主役化」「テキストの見切れ・はみ出し」
 * 「FontAwesome の未定義アイコン」「ショートで禁止されている見開き・図鑑装丁」
 * 「画像パスの規約違反」を計測する。
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
 *   - **いらすとやの隠れ（visibleRatio）**: 主役化とは**逆向き**の失敗。テキストで埋まっている
 *     スライドに `position:absolute` でイラストを敷くと、大半がテキストの下に潜って切れ端だけが
 *     見える状態になる（実際に導入スライド1・2で発生）。イラストを格子状にサンプリングし、
 *     `elementsFromPoint` のスタックで「手前に、その点を実際に塗っている要素があるか」を見て、
 *     見えている点の割合を可視率として出す。母数は canvas で取った**絵のある画素**だけに絞る
 *     （いらすとやの PNG は透明余白が広く、そこへの重なりまで数えると良品と不良品が同値に潰れる）。
 *     面積判定はイラストが小さく・隠れるほど合格に近づくため、この失敗は既存の3判定のどれにも
 *     掛からず、目視でしか気づけなかった。
 *   - **見切れ（clipped）**: `overflow` が visible 以外の要素で `scrollWidth/Height` が
 *     `clientWidth/Height` を超えるもの。実際にブラウザが内容を切り落としている状態そのもの。
 *     入れ子で親子とも該当する場合は、原因に近い最内側の要素だけを残す。
 *   - **はみ出し（outOfBounds）**: 内容領域の外へ出ている要素。`.page` の padding-bottom は
 *     字幕帯用に空けた紙面（SKILL.md §10「本の下端より下は字幕帯」）なので、ここへ本文が
 *     侵入していれば検出される。
 *   - **未定義アイコン（brokenIcons）**: `fa-solid` 等のスタイルクラスを持つ要素のうち、
 *     `::before` の content が空のもの。FontAwesome は具体名のクラス（`.fa-xxx:before`）で
 *     content を与えるので、Free に無い名前（`fa-gauge-simple-low` などの Pro 限定アイコン）や
 *     綴り間違いを書くと**何のエラーも出ずにアイコンだけが消える**。要素は幅0になるだけで
 *     レイアウトも崩れないため、上の3つの判定にも掛からず目視でしか気づけなかった
 *     （実際に Slide 4-1 で1つ欠けたまま出荷寸前まで気づけなかった）。
 *   - **画像パス（imagePaths）**: `.slide-container` 配下の全 `<img>` について、ブラウザが
 *     絶対 URL に正規化する `element.src` ではなく `getAttribute('src')` の生値を調べる。
 *     `public/` 始まり以外の参照は、ローカルの `file://` キャプチャで偶然表示できても
 *     別マシンや CI で再現しないため違反として報告する。
 */

/** ブラウザ内で実行される計測関数の本体（page.evaluate に渡す）。 */
const measureInPage = (slideSelector, index, opts) => {
    const { excludeSelectors, illustrationSrcPattern, tolerancePx, boundsTolerancePx, visibilitySampleSteps } = opts;
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

    const containsPoint = (r, x, y) => x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;

    /**
     * その点で「実際に何かを描いている」要素か。
     *
     * **要素の box をそのまま塗りつぶし扱いにしてはいけない。** 中央寄せの見出し（`.std-copy` /
     * `h1`）はテキストが中央にあってもブロックの box は全幅に広がるので、box で判定すると
     * 右下に置いたイラストが「テキストに覆われている」と誤判定される（良品デッキ2本で
     * 可視率 0.145 / 0.245 と出た。目視ではイラストは完全に見えている）。
     * そこでテキストは `Range.getClientRects()` で**実際の行ボックス（グリフの並び）**を取り、
     * 背景・画像は box で判定する。
     */
    const paintsAt = (el, x, y) => {
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || Number(style.opacity) === 0) return false;

        // 不透明・半透明の背景色や背景画像を持つ要素（チップ・帯・カード）は box 全体を塗る。
        const bgAlpha = (style.backgroundColor.match(/rgba?\(([^)]+)\)/) || [])[1];
        const alpha = bgAlpha ? Number(bgAlpha.split(',')[3] ?? 1) : 0;
        if (alpha > 0.1) return true;
        if (style.backgroundImage && style.backgroundImage !== 'none') return true;
        // 画像・アイコングリフ（::before で描く FontAwesome）は自身の box を塗るとみなす。
        if (el.tagName.toLowerCase() === 'img' || el.tagName.toLowerCase() === 'svg') return true;
        if (!isEmptyContent(getComputedStyle(el, '::before').content)) return true;

        // 直接のテキストノードは、行ボックス（グリフの実際の位置）に点が入るときだけ塗る。
        for (const node of el.childNodes) {
            if (node.nodeType !== 3 || !node.nodeValue.trim()) continue;
            const range = document.createRange();
            range.selectNodeContents(node);
            for (const r of range.getClientRects()) {
                if (containsPoint(r, x, y)) return true;
            }
        }
        return false;
    };

    /**
     * `<img>` の**実際に絵が描かれている画素**（alpha > 0）のマスクを、要素の box と同じ座標系で作る。
     *
     * いらすとやの PNG は四辺（と多くは中央付近も）に広い透明余白を持つ。矩形をそのまま母数にすると
     * 「透明な部分に他要素が重なっただけ」で可視率が下がり、良品と不良品が同じ値に潰れる
     * （実測: 良品 0.735 / 不良品 0.733）。そこで母数を「絵のある画素」に絞る。
     *
     * `object-fit: contain` によるレターボックスを含めて box 座標へ写すため、box と同じ大きさの
     * canvas に contain 相当の矩形で描く。file:// の画像は canvas を汚染するので、
     * `--allow-file-access-from-files` 付きで起動していない場合は `getImageData` が例外になる。
     * その場合は null を返し、呼び出し側は矩形全体を母数にしたフォールバックで測る。
     */
    const drawnAlphaMask = (img, width, height) => {
        const w = Math.max(1, Math.round(width));
        const h = Math.max(1, Math.round(height));
        const natW = img.naturalWidth;
        const natH = img.naturalHeight;
        if (!natW || !natH) return null;

        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        if (!ctx) return null;

        // object-fit の既定は fill だが、このデッキ群では contain を使うため両方に対応する。
        const fit = getComputedStyle(img).objectFit;
        if (fit === 'contain' || fit === 'scale-down') {
            const scale = Math.min(w / natW, h / natH);
            const dw = natW * scale;
            const dh = natH * scale;
            ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
        } else if (fit === 'cover') {
            const scale = Math.max(w / natW, h / natH);
            const dw = natW * scale;
            const dh = natH * scale;
            ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
        } else {
            ctx.drawImage(img, 0, 0, w, h);
        }

        try {
            return { data: ctx.getImageData(0, 0, w, h).data, width: w, height: h };
        } catch {
            return null; // canvas が汚染されている（file:// アクセス許可なしで起動）
        }
    };

    /**
     * 要素が他要素に覆われずに見えている面積の割合（可視率）を測る。
     *
     * 矩形を `visibilitySampleSteps` × `visibilitySampleSteps` の格子に割り、各セルの中心で
     * `document.elementsFromPoint`（重なり順に並んだスタック）を取る。対象より手前にある要素の
     * うち、その点で実際に描いているもの（`paintsAt`）が1つでもあれば、その点は覆われている。
     * 重なり順の解釈はブラウザに任せるので、z-index / DOM順 / stacking context を自前で
     * 解釈する必要がない。
     *
     * 母数は**絵が描かれている点だけ**（`drawnAlphaMask`）。マスクが取れない環境では矩形全体を
     * 母数にフォールバックし、その旨を `maskUsed:false` で返す（透明余白のぶん厳しめに出る）。
     *
     * ビューポート外・hit-test に現れない点は**母数から除く**（覆われている扱いにしない）。
     * 全点が除かれた場合は測定不能として null を返し、判定対象から外す。
     */
    const visibleRatioOf = (el, rect, elementRect) => {
        const width = rect.right - rect.left;
        const height = rect.bottom - rect.top;
        if (width <= 0 || height <= 0) return { ratio: null, maskUsed: false };

        const mask = el.complete ? drawnAlphaMask(el, elementRect.width, elementRect.height) : null;
        const alphaAt = (x, y) => {
            if (!mask) return 255;
            const mx = Math.floor(((x - elementRect.left) / elementRect.width) * mask.width);
            const my = Math.floor(((y - elementRect.top) / elementRect.height) * mask.height);
            if (mx < 0 || my < 0 || mx >= mask.width || my >= mask.height) return 0;
            return mask.data[(my * mask.width + mx) * 4 + 3];
        };

        let sampled = 0;
        let visible = 0;
        for (let i = 0; i < visibilitySampleSteps; i++) {
            const x = rect.left + ((i + 0.5) * width) / visibilitySampleSteps;
            if (x < 0 || x >= window.innerWidth) continue;
            for (let j = 0; j < visibilitySampleSteps; j++) {
                const y = rect.top + ((j + 0.5) * height) / visibilitySampleSteps;
                if (y < 0 || y >= window.innerHeight) continue;
                if (alphaAt(x, y) < 128) continue; // 絵が無い（透明な）点は母数に入れない
                const stack = document.elementsFromPoint(x, y);
                const selfIndex = stack.indexOf(el);
                if (selfIndex === -1) continue; // hit-test に現れない＝測れない点
                sampled++;
                if (!stack.slice(0, selfIndex).some((above) => paintsAt(above, x, y))) visible++;
            }
        }
        return { ratio: sampled === 0 ? null : visible / sampled, maskUsed: Boolean(mask), sampled };
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

    /**
     * FontAwesome の「スタイルクラス」。これを持つ要素はアイコンを描くつもりの要素とみなす。
     * FA6（fa-solid 等）と FA5 の旧記法（fas/far/fab）の両方を拾う。
     */
    const FA_STYLE_CLASS = /^(fa-(solid|regular|brands|light|thin|duotone|sharp|classic)|fa[srlbd]?)$/;
    const isIconEl = (el) => Array.from(el.classList).some((c) => FA_STYLE_CLASS.test(c));
    /** content が実質空＝グリフが出ていない状態。ブラウザ差を吸収して判定する。 */
    const isEmptyContent = (v) => !v || v === 'none' || v === 'normal' || v === '""' || v === "''";

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
        const brokenIcons = [];

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

            // --- FontAwesome の未定義アイコン ---
            // **必ず下の「幅0ならスキップ」より前に置く。** グリフが出ないアイコンは
            // 幅0になるため、後ろに置くと検出対象から漏れる。
            if (isIconEl(el) && isEmptyContent(getComputedStyle(el, '::before').content)) {
                const classes = Array.from(el.classList);
                brokenIcons.push({
                    label,
                    path: describe(el),
                    classes: classes.join(' '),
                    // スタイルクラスを除いた「アイコン名」候補。差し替え対象を示す。
                    iconClasses: classes.filter((c) => c.startsWith('fa-') && !FA_STYLE_CLASS.test(c)),
                });
            }

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
                const visible = visibleRatioOf(el, clippedRect, rect);
                illustrationImages.push({
                    src: (el.getAttribute('src') || '').split('/').pop(),
                    widthRatio: Number(((clippedRect.right - clippedRect.left) / box.width).toFixed(3)),
                    heightPx: Math.round(clippedRect.bottom - clippedRect.top),
                    // 絵のある画素のうち、他要素に覆われず見えている割合
                    //（§7・§9「隠れたイラストは置かない」の判定用）
                    visibleRatio: visible.ratio === null ? null : Number(visible.ratio.toFixed(3)),
                    // 絵の画素マスクを使えたか（false のときは矩形全体が母数＝厳しめの値）
                    visibleRatioMasked: visible.maskUsed,
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
            brokenIcons,
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
    let brokenIcons = [];

    // 可視率は hit-test で測るので、計測前に次の2つを整える（どちらも描画には影響しないので
    // スクリーンショットの結果は変わらない）。
    //   1. 対象スライドをビューポート中央へスクロールする。`elementFromPoint` はビューポート座標
    //      でしか引けないため、画面外にあるスライドは可視率が測れない（null になる）。
    //   2. `pointer-events:none` を打ち消す。この指定を持つ要素は hit-test をすり抜けるので、
    //      イラストの上に重なっていても「見えている」と誤判定される。
    slide.scrollIntoView({ block: 'center', inline: 'center' });
    const hitTestStyle = document.createElement('style');
    hitTestStyle.textContent = '*{pointer-events:auto!important}';
    document.head.appendChild(hitTestStyle);

    try {
        for (const [el, label] of targets) {
            const result = measurePage(el, label, pageEls.length > 0);
            if (!result) continue;
            pages.push(result.page);
            clipped = clipped.concat(result.clipped);
            outOfBounds = outOfBounds.concat(result.outOfBounds);
            brokenIcons = brokenIcons.concat(result.brokenIcons);
        }
    } finally {
        // 同じ page で後続スライドを撮影するので、副作用を必ず戻す。
        hitTestStyle.remove();
    }

    return { pages, clipped, outOfBounds, brokenIcons, isSpread: pageEls.length > 0 };
};

/** ショートで禁止されている見開き構造・図鑑装丁を DOM から検出する。 */
const measureShortSpreadInPage = (slideSelector, index) => {
    const slide = document.querySelectorAll(slideSelector)[index];
    if (!slide) return null;

    const pageCount = slide.querySelectorAll('.page').length;
    const hasLeftAndRight = Boolean(slide.querySelector('.page.left') && slide.querySelector('.page.right'));
    const spreadBaseClasses = ['short-spread', 'paper-slide', 'paper-grain'];
    const classes = spreadBaseClasses.filter(
        (className) => slide.classList.contains(className) || slide.querySelector(`.${className}`),
    );

    const reasons = [];
    if (pageCount >= 2 || hasLeftAndRight) reasons.push('見開き構造');
    if (classes.length > 0) reasons.push('図鑑装丁クラス');

    return {
        reasons,
        evidence: {
            pageCount,
            hasLeftAndRight,
            classes,
        },
    };
};

/** スライド内の画像が `public/` 始まりの素直な相対パスだけを使っているか検出する。 */
const measureImagePathsInPage = (slideSelector, index) => {
    const slide = document.querySelectorAll(slideSelector)[index];
    if (!slide) return null;

    const violations = [];
    for (const image of slide.querySelectorAll('img')) {
        const src = image.getAttribute('src') || '';
        const reasons = [];

        if (/^file:\/\//i.test(src)) reasons.push('file:// URI');
        if (src.startsWith('/')) reasons.push('絶対パス');
        if (/^https?:\/\//i.test(src)) reasons.push('外部URL');
        if (src.includes('..')) reasons.push('.. を含むパッケージ外参照');
        if (reasons.length === 0 && !src.startsWith('public/')) {
            reasons.push('public/ で始まらない相対パス');
        }

        if (reasons.length > 0) violations.push({ reasons, src });
    }
    return violations;
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
    /**
     * 可視率のサンプリング分割数（縦横それぞれ）。40 なら最大1600点。絵のある画素だけを母数に
     * するとサンプル数が目減りするので、粗くしすぎない（いらすとやは 200〜300px 角程度なので、
     * 1点あたり数 px 四方の粒度になる）。
     */
    visibilitySampleSteps: 40,
};

/**
 * 1スライドのレイアウトを計測する。
 * @returns {Promise<{pages:object[], clipped:object[], outOfBounds:object[], brokenIcons:object[], isSpread:boolean}>}
 */
export async function measureSlideLayout(page, slideSelector, index, options = DEFAULT_LAYOUT_OPTIONS) {
    const merged = { ...DEFAULT_LAYOUT_OPTIONS, ...options };
    return (
        (await page.evaluate(measureInPage, slideSelector, index, merged)) || {
            pages: [],
            clipped: [],
            outOfBounds: [],
            brokenIcons: [],
            isSpread: false,
        }
    );
}

/**
 * ショート1スライドに、長尺専用の見開き構造・図鑑装丁が使われていないかを計測する。
 * 呼び出し側で short モードのときだけ実行する。
 *
 * @returns {Promise<{reasons:string[], evidence:{pageCount:number, hasLeftAndRight:boolean, classes:string[]}}>}
 */
export async function measureShortSpread(page, slideSelector, index) {
    return (
        (await page.evaluate(measureShortSpreadInPage, slideSelector, index)) || {
            reasons: [],
            evidence: {
                pageCount: 0,
                hasLeftAndRight: false,
                classes: [],
            },
        }
    );
}

/**
 * 1スライド内の画像パス規約違反を計測する。
 * long / short の両モードで呼び出す。
 *
 * @returns {Promise<{reasons:string[], src:string}[]>}
 */
export async function measureImagePaths(page, slideSelector, index) {
    return (await page.evaluate(measureImagePathsInPage, slideSelector, index)) || [];
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
 * 他要素の下に潜って隠れているいらすとや画像を抽出する。
 *
 * 対応する規則: §7「テキストで埋まっているスライドにいらすとやを無理に置かない。8割以上見せられる
 * 空きが確保できないなら置かない」／§9「隠れたイラストを置くくらいなら無いほうが良い」。
 *
 * `findIllustrationDominant` と**逆向き**の失敗を見る。イラストが小さく・隠れているほど面積比は
 * 下がるため主役化判定は必ず合格になり、この失敗は既存の判定では検出できない。
 *
 * 校正（2026-08-11。良品＝評価ループを通過して納品済みのデッキ＝全ページ合格が正解）:
 *   不良例（LINEMO 衛星通信デッキの修正前。「いらすとやが完全に隠れている」とユーザー指摘を受けた版）
 *     スライド1 std: business_man2_3_surprise.png 0.532
 *     スライド2 std: present_open.png             0.679
 *   良品
 *     video/long-39（ahamo 増量）  スライド1/2/3: 0.979 / 0.998 / 1
 *     video/long-38（無制限比較）  スライド1・6-2: 0.975 / 1
 *     video/long-37（LINEMOトライアル）スライド1/2: 1 / 1
 *     video/long-41 の前デッキ（89枚）いらすとや6枚: 全て 1
 *   良品は 0.975 以上、不良例は 0.68 以下と大きく開くので、閾値は SKILL.md §7 の目安と同じ
 *   **0.8**（8割見えているか）に置く。両側に十分な余裕がある。
 *
 * なお、絵の画素マスクを使えなかった測定（`visibleRatioMasked !== true`。ブラウザを
 * `--allow-file-access-from-files` なしで起動した場合）は、透明余白まで母数に入って
 * 不当に低く出るため**判定しない**（上記の校正でも、マスク無しでは良品が 0.735 まで落ちて
 * 不良例 0.733 と見分けが付かなかった）。
 *
 * @param {{id:string, pages:object[]}[]} results
 */
export function findIllustrationOccluded(results, { minVisibleRatio = 0.8 } = {}) {
    const occluded = [];
    for (const { id, pages } of results) {
        for (const p of pages || []) {
            for (const img of p.illustrationImages || []) {
                // 測定不能（ビューポート外など）・マスク無しの測定は判定対象から外す。
                if (typeof img.visibleRatio !== 'number') continue;
                if (img.visibleRatioMasked !== true) continue;
                if (img.visibleRatio >= minVisibleRatio) continue;
                occluded.push({ id, label: p.label, src: img.src, visibleRatio: img.visibleRatio });
            }
        }
    }
    return occluded;
}

/**
 * 絵の画素マスクが使えず、可視率の判定をスキップした画像を数える。
 *
 * `--allow-file-access-from-files` の付け忘れなどで判定が黙って無効化されるのを防ぐため、
 * キャプチャ時に件数を表示する。
 *
 * @param {{id:string, pages:object[]}[]} results
 */
export function countUnmaskedIllustrations(results) {
    let count = 0;
    for (const { pages } of results) {
        for (const p of pages || []) {
            for (const img of p.illustrationImages || []) {
                if (typeof img.visibleRatio === 'number' && img.visibleRatioMasked !== true) count++;
            }
        }
    }
    return count;
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

/**
 * 未定義の FontAwesome アイコンをスライド横断で集計する。
 *
 * 対応する規則: SKILL.md §9「FontAwesome のアイコン名は Free 版に存在するものだけ使う」。
 * Pro 限定アイコン（`-low` などの階調バリエーション）や綴り間違いを書くと、エラーは出ず
 * アイコンだけが黙って消える。
 *
 * @param {{id:string, brokenIcons?:object[]}[]} results
 */
export function collectBrokenIcons(results) {
    const broken = [];
    for (const r of results) {
        for (const b of r.brokenIcons || []) broken.push({ id: r.id, ...b });
    }
    return broken;
}

/**
 * ショートで禁止されている見開き構造・図鑑装丁の検出結果をスライド横断で集計する。
 *
 * 対応する規則: generate-short-slides の SKILL.md §0「見開き（2ページ）構成はショートでは
 * 使用禁止」「装丁（見た目）も長尺と共用しないこと」。
 *
 * @param {{id:string, shortSpread?:{reasons:string[], evidence:object}}[]} results
 */
export function collectShortSpreadViolations(results) {
    const violations = [];
    for (const r of results) {
        if (!r.shortSpread || r.shortSpread.reasons.length === 0) continue;
        violations.push({ id: r.id, ...r.shortSpread });
    }
    return violations;
}

/**
 * `public/` 始まりでない画像パスの検出結果をスライド横断で集計する。
 *
 * 対応する規則: generate-short-slides の SKILL.md §4「画像パスは `public/` 始まりの
 * 相対パス。絶対パス・`file://`・他パッケージ参照は禁止」。
 *
 * @param {{id:string, imagePaths?:{reasons:string[], src:string}[]}[]} results
 */
export function collectImagePathViolations(results) {
    const violations = [];
    for (const r of results) {
        for (const violation of r.imagePaths || []) {
            violations.push({ id: r.id, ...violation });
        }
    }
    return violations;
}
