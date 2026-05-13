Generate HTML presentation slides for YouTube shorts (1:1 aspect ratio) based on a script, applying an ultra-bold, high-impact design suitable for smartphone viewing.

Script file path: $ARGUMENTS (default: `台本.txt`)

---

# Generate YouTube Shorts HTML Slides

When generating HTML slides for YouTube shorts from a script (e.g., `台本.txt`), adhere strictly to the following design and structural requirements.

## 1. Output Format & Structure
- **Output File**: Default to `slides-short.html` unless specified otherwise.
- **Slide Class**: Every slide `<div>` **must** use the class `slide-container`. The capture script (`capture_slides_html.js`) locates slides by querying `.slide-container`, so any slide missing this class will be skipped.
- **Aspect Ratio**: 1:1 (`width: 1080px; height: 1080px;`).
- **Layout**: Center content, use flexbox (`flex-row`, `flex-col`).
- **Base Color scheme**: Trustworthy Blue (`#0052cc`), White (`#ffffff`), and Red (`#e63946`) for emphasis. Background outside slides: `#f0f4f8`. Slide background: `#ffffff`.

## 2. Typography
- **Fonts**: 'Inter', 'Noto Sans JP', sans-serif. Ensure Google Fonts are imported.
- **Weights**: Extremely bold (`700` or `900`) for readability on small smartphone screens.
- **Rule**: Eliminate long sentences. Extract only the shortest, most impactful phrases (e.g., "30GB", "たったの2,970円", "通話無料") from the script.
- **Do NOT over-abbreviate established compound nouns**: Terms like `通信品質`、`乗り換えキャンペーン` must be kept intact. Dropping a character to shorten (e.g., `通信品質` → `品質`) changes the meaning and feels unnatural.

## 3. Mandatory Slide Types
Ensure you iterate through the exact number of `スライドID` found in the script.

### A. Thumbnail Slide (Slide 1)
- **Background**: `repeating-radial-gradient(circle at 50% 50%, #ffffff 0%, #f0f7ff 10%, #e6f0ff 20%)` with a `25px solid #0052cc` border.
- **Logo Area**: Include ONLY when the video features a single carrier. Omit entirely when the video is a comparison (e.g., "A vs B"). Logo `<img>` height: `150px`. Wrapper height: `190px`.
- **Catchphrase layout**: `gap: 26px` between elements. Add `style="margin-bottom: 250px;"` to `.catchphrase-wrapper` to reserve space for the bottom-right illustration and prevent overlap.
- **Tag (e.g., 「無料」)**: `font-size: 70px`, rotated (`transform: rotate(-3deg)`), red background `#e63946`, `padding: 14px 46px`, `box-shadow: 6px 6px 0 #000`.
- **Main title**: `font-size: 90px`.
- **Sub-title band**: `font-size: 56px`, `padding: 14px 38px`.
- **Badge (e.g., メトロ)**: `font-size: 48px`, `padding: 12px 36px`.
- **Illustration**: Bottom-right absolute, `height: 290px`, `filter: drop-shadow(...)`.

### B. Standard Explanation Slides (Slide 2 - Penultimate Slide-1)
- Include watermark-style numbering at the top-left (`font-size: 280px`, opacity `0.07`).
- **Slide title** (`slide-title`): `font-size: 62px`, bottom border `border-bottom: 10px solid #0052cc`, `margin-bottom: 30px`.
- **Slide body** (`slide-body`): `gap: 28px` between items. When illustration overlaps body content, add `style="margin-bottom: 120px;"` to `.slide-body`.
- **List items** (`.list-item`): `font-size: 52px`, emoji `font-size: 54px`.
- **Info box** (`.info-box`): label `font-size: 40px`, value `font-size: 64px`, `padding: 22px 32px`.
- **Highlight block** (`.highlight-block`): `font-size: 62px`, `padding: 20px 24px`.
- **Date badge** (`.date-badge`): `font-size: 40px`, `padding: 10px 30px`.
- **Illustration**: Bottom-right absolute, `height: 260px`. Always add `style="z-index: 2;"` to the `.slide-illust` wrapper div so the illustration renders above all other elements.
- Use emojis for list items instead of standard bullets.

### C. Warning Slide (Penultimate Slide)
- **Theme**: Red / Faint Red (`background: #fff8f8`).
- **Warning banner**: `font-size: 62px`, `padding: 22px 0`, full-bleed across slide.
- **Warning box**: `border: 10px solid #e63946; background: #fff0f0;`, `padding: 36px 42px`, `gap: 26px`.
  - Box title (`.w-title`): `font-size: 58px`.
  - Box items (`.w-item`): `font-size: 50px`.
- **Illustration**: Bottom-right absolute, `height: 280px`. Use a shocked-expression illustration.

### D. CTA Slide (Last Slide)
- **Theme**: `background: linear-gradient(135deg, #0052cc, #003380)`.
- **Logo**: `height: 120px`, `margin-bottom: 26px`, `filter: brightness(10)` to make it white.
- **Title** (`.cta-title`): `font-size: 84px`, color `#ffd700`.
- **Sub-text** (`.cta-sub`): `font-size: 50px`, color `#ffffff`.
- **Bounce arrow**: `font-size: 90px`, color `#ffd700`, `@keyframes bounce` animation.
- **Banner image** (`.cta-banner-img`): `width: 940px`. Use the video's own thumbnail from `public/images/thumbnails/` — the file follows the naming convention `{動画タイトル}_サムネ1.png`. Do NOT use generic slides images (e.g. `public/images/slides/今すぐ本編動画をチェック.png`).

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
- **Overflow Check**: Before final generation, strictly verify that all text and images fit entirely within the `1080px × 1080px` container.
- **Automatic Adjustment Rules**:
    - **Text**: Even after refining to short phrases, if text still overflows, reduce the font size by 10%–15% from the standard sizes defined above.
    - **Images**: If illustrations overlap text making it unreadable, reduce the image height or adjust position — but never go below 200px for slide illustrations.
- **Mobile Visibility**: Since the 1:1 aspect ratio will be viewed full-screen on smartphones, ensure sufficient margins (safe areas) at the edges.
- **Fill the canvas**: The standard sizes above are the baseline — the goal is a visually full, high-impact canvas with minimal empty space. If a slide feels sparse, increase font or image sizes rather than adding padding.
