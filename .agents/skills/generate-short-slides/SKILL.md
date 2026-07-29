---
name: generate-short-slides
description: "Generate HTML presentation slides for YouTube shorts (1:1 aspect ratio) based on a script, applying an ultra-bold, high-impact design suitable for smartphone viewing."
---

Script file path: $ARGUMENTS (default: `台本.txt`)

---

# Generate YouTube Shorts HTML Slides

When generating HTML slides for YouTube shorts from a script (e.g., `台本.txt`), adhere strictly to the following design and structural requirements.

## 0. 着手前に「直近の完成ショートデッキ」を必ず読む

**ゼロから発明しない。** 生成に着手する前に、直近のショート動画で完成・納品済みのスライドを読み、構成と部品の使い方をそのまま踏襲する。これを飛ばすと毎回レイアウトが作り直しになり、同じ手直し指摘を繰り返すことになる（実績あり）。

```bash
git branch -a | grep 'video/short-'                          # 直近のショートブランチを確認
git show "<branch>:slides-short.html" | grep -n 'Slide ID'    # 構成（何を何枚で見せたか）を俯瞰
git show "<branch>:slides-short.html"                         # 実装を読む
```

### 🚫 見開き（2ページ）構成はショートでは使用禁止

ノート見開き・図鑑見開き（`spread-base.css` / `.short-spread` / 1つの `.slide-container` 内に `.page.left` と `.page.right` を並べる構成）は**長尺専用**である。ショートは以下の理由で必ず**1スライド＝1画面の単ページ構成**にする:

- ショートはスマホ全画面の縦長で視聴され、1080×1080 を左右に割ると文字が半分のサイズになって読めない。
- 1枚あたりの表示時間が数秒しかないため、左右2ページ分の情報量は処理しきれない。

**装丁（見た目）も長尺と共用しないこと。** `templates/spread-base.css` の紙テクスチャ・ノート罫線・製本枠（`.paper-slide` / `.paper-grain` / 濃茶の外枠）は図鑑見開き用であり、ショートでは使わない。ショートは §1 の配色（`body: #f0f4f8` / `.slide-container: #ffffff`）に従った**白背景＋青赤アクセント**が正。構成だけ単ページにして装丁を図鑑のまま残すのも不可。

ショートの標準構成（直近デッキで確立済み。これを踏襲する）:

| スライド | クラス | 構成 |
|---|---|---|
| 1枚目 | `slide-container slide-thumbnail` | 表紙。大見出し＋集中線背景＋バッジ |
| 中間 | `slide-container`（＋料金を出すなら `price-note`） | `.watermark`（連番）→ `h2.slide-title` → `.slide-body`（`.info-card` / `.fee-grid` 等のカード群）→ `.slide-illust`（右下・脇役） |
| 注意喚起 | `slide-container warning-slide` | `.warning-banner` → `.warning-title` → `.warning-box` |
| 最終 | `slide-container cta-slide` | `.cta-content` 内に logo → title → sub → banner → arrow を**縦積み**（§3 F 参照） |

## 1. Output Format & Structure
- **Output File**: Default to `slides-short.html` unless specified otherwise.
- **Slide Class**: Every slide `<div>` **must** use the class `slide-container`. The capture script (`capture_slides_html.js`) locates slides by querying `.slide-container`, so any slide missing this class will be skipped.
- **Aspect Ratio**: 1:1 (`width: 1080px; height: 1080px;`).
- **Layout**: Center content, use flexbox (`flex-row`, `flex-col`).
- **Base Color scheme**: Trustworthy Blue (`#0052cc`), White (`#ffffff`), and Red (`#e63946`) for emphasis. Background outside slides: `#f0f4f8`. Slide background: `#ffffff`.
- **料金表記コンプライアンス（アクセストレード要請）**: 料金が「月額・税込」である旨の注記パーツ。以下の `::after` ルールを `<style>` に**必ず**含めること（文言・配置は変更しない）。表示はオプトインで、**料金（円・月額など）を表示するスライドの `<div class="slide-container ...">` に `price-note` クラスを足したときだけ**注記が出る（例: `<div class="slide-container price-note">`）。料金を出さないスライドには付けない:
```css
.slide-container.price-note::after {
    content: "※表示している料金はすべて月額・税込みの価格です";
    position: absolute; right: 20px; bottom: 16px; z-index: 9999;
    background: rgba(0,0,0,0.62); color: #fff;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 26px; font-weight: 700; letter-spacing: 0.02em; line-height: 1;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap; pointer-events: none;
}
```

## 2. Typography
- **Fonts**: 'Inter', 'Noto Sans JP', sans-serif. Ensure Google Fonts are imported.
- **Weights**: Extremely bold (`700` or `900`) for readability on small smartphone screens.
- **Rule**: Eliminate long sentences. Extract only the shortest, most impactful phrases (e.g., "30GB", "たったの2,970円", "通話無料") from the script.
- **Do NOT over-abbreviate established compound nouns**: Terms like `通信品質`、`乗り換えキャンペーン` must be kept intact. Dropping a character to shorten (e.g., `通信品質` → `品質`) changes the meaning and feels unnatural.

## 3. Mandatory Slide Types
Ensure you iterate through the exact number of `スライドID` found in the script.

### A. Thumbnail Slide (Slide 1)

**Background**: Sunburst radial pattern — layer a `repeating-conic-gradient` over a radial gradient for visual energy:
```css
background:
    repeating-conic-gradient(from 0deg at 52% 48%, rgba(0,82,204,0.06) 0deg 2.5deg, transparent 2.5deg 16deg),
    radial-gradient(ellipse at 52% 48%, #ffffff 5%, #e8f3ff 45%, #c8dcff 100%);
```
Add a `25px solid #0052cc` border and `padding-top: 160px; padding-bottom: 300px;` to center content in the upper zone and prevent overlap with the bottom-right illustration. **`padding-top` must be at least `140px`** — the `thumb-top-strip` is absolute-positioned at `top: 25px` with `font-size: 36px` and `padding: 18px 0`, so it occupies roughly `25px → 115px` from the top edge; anything less than `140px` causes the first flex child (e.g. `.thumb-tag`) to overlap the strip.

**Top announcement strip**: Always add a full-width blue band just inside the border:
```css
.thumb-top-strip {
    position: absolute; top: 25px; left: 25px; right: 25px;
    background: var(--blue); color: #fff;
    font-size: 36px; font-weight: 900; padding: 18px 0;
    text-align: center; letter-spacing: 0.06em; z-index: 3;
}
```
Fill it with a short topic label (e.g., `⚡ 2026年4月 最新通信品質調査 ⚡`).

**Corner accent triangles** (optional but recommended for energy):
```css
.thumb-accent-tri.tl { top:25px; left:25px; border-top:300px solid rgba(0,82,204,0.09); border-right:300px solid transparent; }
.thumb-accent-tri.br { bottom:25px; right:25px; border-bottom:300px solid rgba(0,82,204,0.09); border-left:300px solid transparent; }
```

**Tag (e.g., 「最下位！」)**: `font-size: 80px`, rotated (`transform: rotate(-3deg)`), red background `#e63946`, `padding: 18px 54px`, `box-shadow: 8px 8px 0 rgba(0,0,0,0.25)`, `margin-bottom: 28px`.

**Main title**: `font-size: 80px`, `line-height: 1.25`, `margin-bottom: 22px`, `max-width: 900px`.

**Rank number row** (use when the content is a ranking — e.g., "4キャリア中最下位"): Show a large italic rank number with a label block beside it:
```html
<div class="thumb-rank-row">
    <span class="rank-num-big">4</span>   <!-- font-size:150px, color:red, italic -->
    <div class="rank-denom-block">         <!-- border-left:6px solid red, padding-left:16px -->
        <span class="rank-over-label">4キャリア中</span>   <!-- 44px, dark -->
        <span class="rank-pos-label">最下位確定</span>     <!-- 50px, red -->
    </div>
</div>
```

**Sub-title band**: `font-size: 60px`, `padding: 18px 70px`, `border-radius: 12px`, `box-shadow: 4px 4px 0 rgba(0,0,0,0.2)`.

**Logo Area**: Include ONLY when the video features a single carrier. Omit entirely when the video is a comparison (e.g., "A vs B"). Logo `<img>` height: `150px`. Wrapper height: `190px`.

**Illustration**: Bottom-right absolute, `height: 290px`, `filter: drop-shadow(...)`. Because `padding-bottom: 300px` reserves vertical space, the illustration will not overlap the text content.

### B. Standard Explanation Slides (Slide 2 - Penultimate Slide-1)
- Include watermark-style numbering at the top-left (`font-size: 280px`, opacity `0.07`).
- **Slide title** (`slide-title`): `font-size: 62px`, bottom border `border-bottom: 10px solid #0052cc`, `margin-bottom: 30px`.
- **Slide body** (`slide-body`): `gap: 28px` between items. When illustration overlaps body content, add `style="margin-bottom: 120px;"` to `.slide-body`.
- **Illustration**: Bottom-right absolute, `height: 260px`. Always add `style="z-index: 2;"` to the `.slide-illust` wrapper div so the illustration renders above all other elements.
- Use emojis for list items instead of standard bullets.

**Info card style** (preferred over plain `.list-item` when showing sourced data or key facts — produces a richer, card-based layout):
```css
/* Optional header card for sourced reports */
.report-header-card {
    display: flex; align-items: center; gap: 24px;
    background: linear-gradient(135deg, #0052cc, #003fa0);
    color: #fff; border-radius: 20px; padding: 28px 36px;
}
/* Fact rows */
.info-card {
    display: flex; align-items: center; gap: 22px;
    padding: 22px 32px; border-radius: 0 16px 16px 0;
    font-size: 46px; font-weight: 700;
    background: #f0f5ff; border-left: 14px solid #0052cc;
}
.info-card.alert {
    background: #fff0f0; border-left-color: #e63946;
    color: #e63946; font-size: 50px; font-weight: 900;
}
```
Use `.info-card.alert` for the single most shocking or important fact on the slide.

**Plain list items** (`.list-item`): `font-size: 52px`, emoji `font-size: 54px`. Use when content is simple and doesn't require card-level emphasis.

**Other elements**:
- **Info box** (`.info-box`): label `font-size: 40px`, value `font-size: 64px`, `padding: 22px 32px`.
- **Highlight block** (`.highlight-block`): `font-size: 62px`, `padding: 20px 24px`.
- **Date badge** (`.date-badge`): `font-size: 40px`, `padding: 10px 30px`.

### C. Ranking Slide
When a slide presents a ranked list (e.g., キャリア通信品質ランキング), **use styled circular number badges** instead of medal emojis. Medal emojis only cover 1st–3rd (🥇🥈🥉) and cannot distinguish ties (e.g., two 🥈 look identical). Use these instead:

```css
.rank-num-badge {
    min-width: 96px; height: 96px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; font-weight: 900; color: #fff; flex-shrink: 0;
}
.rank-num-badge.r1 { background: linear-gradient(135deg, #ffd700, #e6a800); }
.rank-num-badge.r2 { background: linear-gradient(135deg, #b0b8c8, #7a8799); }
.rank-num-badge.r3 { background: linear-gradient(135deg, #cd7f32, #9a5a1a); }
.rank-num-badge.r4 { background: linear-gradient(135deg, #e63946, #b0001e); }
/* Add box-shadow: 3px 3px 0 rgba(0,0,0,0.15) to all */
```

Use `<span class="rank-num-badge r1">1位</span>` through `r4` for each item. The red r4 badge naturally signals "最下位" without extra text (though adding `<span class="rank-worst">最下位</span>` on the last row is also good).

### D. Multi-Option Highlight Slides (e.g., おすすめN選)
When a slide presents N selectable options (e.g., 乗り換え先4選), **split it into N individual slides**, one per option, each highlighting only that option while dimming the others. This keeps viewers engaged through variation.

**Structure**: Keep the same 2×2 (or appropriate) grid on every sub-slide. Apply `.highlighted` to the featured card and `.dimmed` to the rest.

**CSS**:
```css
.recommend-card { position: relative; /* required for spotlight tag */ }

.recommend-card.highlighted {
    border: 8px solid #0052cc;
    transform: scale(1.08);
    box-shadow: 0 20px 50px rgba(0,82,204,0.32);
    background: linear-gradient(155deg, #eaf3ff, #d4e8ff);
    z-index: 4;
}
.recommend-card.dimmed {
    opacity: 0.22;
    filter: grayscale(55%);
}
/* Keyword tag that floats above the highlighted card */
.card-spotlight-tag {
    position: absolute; top: -20px; left: 50%;
    transform: translateX(-50%);
    background: #0052cc; color: #fff;
    font-size: 24px; font-weight: 900;
    padding: 6px 22px; border-radius: 30px;
    white-space: nowrap; box-shadow: 2px 4px 10px rgba(0,0,0,0.2); z-index: 5;
}
/* Progress dots */
.slide-progress { display: flex; gap: 14px; align-items: center; margin: -25px 60px 20px; }
.progress-dot { width: 18px; height: 18px; border-radius: 50%; background: #c0cce0; }
.progress-dot.active { background: #0052cc; width: 26px; height: 26px; }
```

**HTML pattern** (repeat for each option, advancing `.active` dot and swapping `.highlighted` / `.dimmed`):
```html
<div class="slide-container">
    <div class="watermark">4</div>
    <h2 class="slide-title">乗り換え先① mineo</h2>
    <div class="slide-progress">
        <span class="progress-dot active"></span>
        <span class="progress-dot"></span>
        <span class="progress-dot"></span>
        <span class="progress-dot"></span>
    </div>
    <div class="slide-body" style="margin-bottom: 120px;">
        <div class="recommend-grid">
            <div class="recommend-card highlighted">
                <span class="card-spotlight-tag">コスパ最強！</span>
                <img src="..." class="card-logo" alt="mineo">
                <div class="card-desc">月660円〜</div>
            </div>
            <div class="recommend-card dimmed"> ... </div>
            <div class="recommend-card dimmed"> ... </div>
            <div class="recommend-card dimmed"> ... </div>
        </div>
    </div>
    <div class="slide-illust" style="z-index: 10;"> ... </div>
</div>
```

**Spotlight tag wording**: Make it carrier-specific and benefit-focused (e.g., `コスパ最強！` / `基本料¥0！` / `LINEギガフリー！` / `通話かけ放題！`). The title also changes per slide (e.g., `乗り換え先① mineo` → `乗り換え先② povo2.0`).

### E. Warning Slide (Penultimate Slide)
- **Theme**: Red / Faint Red (`background: #fff8f8`).
- **Warning banner**: `font-size: 62px`, `padding: 22px 0`, full-bleed across slide.
- **Warning box**: `border: 10px solid #e63946; background: #fff0f0;`, `padding: 36px 42px`, `gap: 26px`.
  - Box title (`.w-title`): `font-size: 58px`.
  - Box items (`.w-item`): `font-size: 50px`.
- **Illustration**: Bottom-right absolute, `height: 280px`. Use a shocked-expression illustration.

### F. CTA Slide (Last Slide)
- **Theme**: `background: linear-gradient(135deg, #0052cc, #003380)`.
- **Logo**: `height: 110px`, `margin-bottom: 12px`. Show the logo in its **original colors** on a white rounded card so it stays legible on the dark background: `filter: none; background: #fff; border-radius: 18px; padding: 8px 16px; box-shadow: 4px 4px 0 rgba(0,0,0,0.18);`. Do NOT use `filter: brightness(10)` (white-out) — brand logos must keep their original colors.
- **Title** (`.cta-title`): `font-size: 84px`, color `#ffd700`.
- **Sub-text** (`.cta-sub`): `font-size: 50px`, color `#ffffff`.
- **Bounce arrow**: `font-size: 90px`, color `#ffd700`, `@keyframes bounce` animation.
- **Banner image** (`.cta-banner-img`): `width: 940px`, **plus `max-height: 460px; object-fit: contain;`**. The CTA slide stacks logo + title + sub + banner + arrow vertically inside 1080px — verify the banner's bottom edge (and the bounce arrow below it) is fully visible in the rendered PNG. If anything is clipped at the bottom, shrink the banner (`width` down to ~800px) or reduce the title/sub margins until everything fits. ショートは対応する**長尺動画への誘導**なので、バナーには**長尺動画のサムネイル**を使う（ショート自身のサムネは作らない）。探し方:
    1. 入力の短尺台本 CSV は `.../{動画フォルダ}/short/{短尺タイトル}.csv` にある。その2つ上の `{動画フォルダ}/` 直下の `long/` ディレクトリ内にある**長尺台本 CSV のファイル名（拡張子なし）**を取得する。
    2. `public/images/thumbnails/{長尺CSVのファイル名}_サムネ1.png` をバナーに指定する（`public/images/thumbnails/` はマスター `shared/assets/thumbnails/` から `bash scripts/sync-assets.sh` で配布される。長尺サムネが未配布なら同期してから参照する）。
    3. 例: 短尺 `.../34_UQmobile手数料改定/short/UQmobileの手数料….csv` → 長尺 `.../34_UQmobile手数料改定/long/【2026年8月】UQ mobileが手数料を4,950円に値上げ！乗り換え候補3選を徹底解説.csv` → `public/images/thumbnails/【2026年8月】UQ mobileが手数料を4,950円に値上げ！乗り換え候補3選を徹底解説_サムネ1.png`。
    - **該当する長尺サムネが見つからない場合のみ**、フォールバックとして `public/images/slides/今すぐ本編動画をチェック.png` を使う。

## 4. Image Selection & Assets
- **No Placeholders**: Do NOT use placeholder boxes. Always select and use the most appropriate image asset from the `public/images/` directory.
- **Selection Logic**: Analyze the script (e.g., `台本.txt`) to determine the context and select an image from `public/images/GEMINI.md` that matches:
    - **Logos**: Use `public/images/logo/` for MVNO or carrier mentions.
    - **Concepts**: Use `public/images/common/` for general explanations (e.g., congestion, road metaphors).
    - **Emotions/Situations**: Use `public/images/irasutoya/` for reactions (e.g., shock, joy, saving money).
    - **Charts**: Use `public/images/charts/` for data comparisons.
- **Styling**: Apply `object-fit: contain` and `filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1))` to all images.
- **Fallbacks**: If no specific image matches, use a relevant generic illustration from `public/images/irasutoya/` or `public/images/common/`. Do NOT leave images empty.

## 5. Self-Check & Adjustment (Critical)
- **Thumbnail strip/content overlap**: Verify that no flex child on the thumbnail slide (`.thumb-tag`, main title, sub-band, etc.) overlaps with `.thumb-top-strip`. The strip sits at `top: 25px` and is ~90px tall, ending at roughly `y = 115px`. `.slide-thumbnail` must have `padding-top ≥ 140px` so the first child starts below the strip. If overlap is detected, increase `padding-top` (not the strip's `top`) until the gap is clear.
- **Overflow Check**: Before final generation, strictly verify that all text and images fit entirely within the `1080px × 1080px` container.
- **Illustration overlap prevention**: The bottom-right illustration (`position: absolute; bottom: 40px; right: 40px; height: ~260–290px`) occupies roughly the bottom 330px of the slide. On Slide 1, `padding-bottom: 300px` handles this automatically. On other slides, add `style="margin-bottom: 120px;"` to `.slide-body` whenever body content would otherwise extend into that zone.
- **Automatic Adjustment Rules**:
    - **Text**: Even after refining to short phrases, if text still overflows, reduce the font size by 10%–15% from the standard sizes defined above.
    - **Images**: If illustrations overlap text making it unreadable, reduce the image height or adjust position — but never go below 200px for slide illustrations.
- **Mobile Visibility**: Since the 1:1 aspect ratio will be viewed full-screen on smartphones, ensure sufficient margins (safe areas) at the edges.
- **Fill the canvas**: The standard sizes above are the baseline — the goal is a visually full, high-impact canvas with minimal empty space. If a slide feels sparse, increase font or image sizes rather than adding padding.
