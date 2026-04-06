---
name: generate-short-slides
description: Generate HTML presentation slides for YouTube shorts (1:1 aspect ratio) based on a script, applying an ultra-bold, high-impact design suitable for smartphone viewing.
---

# Generate YouTube Shorts HTML Slides

When generating HTML slides for YouTube shorts from a script (e.g., `台本.txt`), adhere strictly to the following design and structural requirements.

## 1. Output Format & Structure
- **Output File**: Default to `slides-short.html` unless specified otherwise.
- **Aspect Ratio**: 1:1 (`width: 1080px; height: 1080px;`).
- **Layout**: Center content, use flexbox (`flex-row`, `flex-col`).
- **Base Color scheme**: Trustworthy Blue (`#0052cc`), White (`#ffffff`), and Red (`#e63946`) for emphasis. Background outside slides: `#f0f4f8`. Slide background: `#ffffff`.

## 2. Typography
- **Fonts**: 'Inter', 'Noto Sans JP', sans-serif. Ensure Google Fonts are imported.
- **Weights**: Extremely bold (`700` or `900`) for readability on small smartphone screens.
- **Rule**: Eliminate long sentences. Extract only the shortest, most impactful phrases (e.g., "30GB", "たったの2,970円", "通話無料") from the script.

## 3. Mandatory Slide Types
Ensure you iterate through the exact number of `スライドID` found in the script.

### A. Thumbnail Slide (Slide 1)
- **Background**: `repeating-radial-gradient(circle at 50% 50%, #ffffff 0%, #f0f7ff 10%, #e6f0ff 20%)` with a `25px solid #0052cc` border.
- **Logo Area**: Large, centered at the top (`height: 180px;`).
- **Catchphrase Text**: Ultra-bold, rotated (e.g., `transform: rotate(-3deg);`), massive text with heavy dropshadows, solid background colors (e.g., Red `#e63946`, Yellow `#ffe600`).
- **Illustration**: Positioned at the bottom (`align-items: flex-end`), using `filter: drop-shadow(...)`.

### B. Standard Explanation Slides (Slide 2 - Penultimate Slide-1)
- Include massive watermark-style numbering at the top-left (e.g., `<div class="big-number">01</div>` overlay with opacity `0.2`).
- Use `slide-title` with bottom blue borders (`border-bottom: 10px solid #0052cc;`).
- **Text blocks**: Use `.highlight-text` with massive `.blue` or `.red` spans to highlight specific metrics (e.g., `30`, `0円`).
- Use emojis for list items instead of standard bullets.

### C. Warning Slide (Penultimate Slide)
- **Theme**: Red / Faint Red to aggressively signify danger/attention.
- **Warning Box**: `border: 10px solid #e63946; background-color: #fff0f0;`
- **Icon/Image**: Shocked expression illustration (e.g., `animal_buta_shock_etc`).

### D. CTA Slide (Last Slide)
- **Theme**: Solid blue gradient background (`linear-gradient(135deg, #0052cc, #003380)`).
- **Text**: Prompt viewers to watch the full video (e.g., "本編で解説！" in yellow `#ffd700`).
- **Animation**: Downward pointing floating arrow (`@keyframes bounce`).
- **Image**: A large `<img>` tag at the bottom for the main YouTube video thumbnail with a blue thick border.

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
    - **Text**: Even after refining to short phrases, if text still overflows, reduce the font size by 10%–15%.
    - **Images**: If background logos or illustrations overlap too much with text making it unreadable, reduce the image size or adjust the position.
- **Mobile Visibility**: Since the 1:1 aspect ratio will be viewed full-screen on smartphones, ensure sufficient margins (safe areas) at the edges.
