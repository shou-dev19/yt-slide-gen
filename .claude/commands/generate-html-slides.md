Generate a presentation slides HTML file based on a script, applying a 'Huge Text' design, specific colors, and image asset mapping.

Script file path: $ARGUMENTS (default: `台本.txt`)

---

# Generate HTML Slides Skill

This skill provides instructions on how to generate "Yukkuri Kaisetsu" style (Japanese commentary style) presentation slides in HTML.

## Design Rules ("Deka-Moji" / Huge Text Style)

To maximize audience retention, use **"Extremely Huge Text Size"** as the standard, ensuring clarity even when viewed on small smartphone screens.

1. **Basic Configuration**
    * **Resolution**: `1280px × 720px`
    * **Font**: Use 'M PLUS Rounded 1c' (Weight: 800/900) for friendliness and high visibility.
    * **Color Palette**: Based on the user-specified theme color, using a white background with borders for consistency.

2. **CSS Style Requirements (Strict Adherence)**
    * **Container**: `.slide-container` { width: 1280px; height: 720px; border: 10px solid var(--primary-color); background: white; box-sizing: border-box; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; flex-shrink: 0; }
    * **Heading (H1)**: Base font size **130px**. Bold. Apply heavy text-shadow (outlining). Example: `text-shadow: 4px 4px 0px white, -4px -4px 0px white, 4px -4px 0px white, -4px 4px 0px white, 0px 4px 0px var(--primary-color), 0px -4px 0px var(--primary-color), 4px 0px 0px var(--primary-color), -4px 0px 0px var(--primary-color);`
    * **Subheading (H2)**: Base font size **90px**. Decorative underline: `border-bottom: 8px solid var(--accent-yellow);`.
    * **Body Text (p, li)**: Base font size **64px**. Line-height 1.4.
    * **Emphasis**: Highlight critical numbers or keywords with `color: var(--accent-red);`. Use `color: var(--text-dark);` for standard text.
    * **Icons**: Use FontAwesome. Size should be large (**100px–200px**).
    * **Lists**: Set `list-style-type: none; padding: 0;` for `ul` to avoid default bullets when using custom icons.

3. **Layout Composition**
    * **Centered Layout**: Default to placing large text and icons in the center.
    * **2-Column Layout (Split)**: Ensure elements remain large and maintain sufficient whitespace.
      `.split { display: flex; width: 100%; justify-content: space-around; align-items: center; }`
      `.split-col { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 20px; }`
    * **Icon-only left column**: When the left `split-col` contains **only** a FontAwesome icon (no text below it), set `style="flex: 0.5"` on that column. This narrows the icon column and gives the right text column more horizontal room. Do NOT add a `<p>` label beneath a standalone icon — the right-column text already provides the explanation.
    * **Tables**: Base font size **50px**. Ensure rows do not overflow the 720px height. Adjust padding and font size meticulously if there are many rows.
    * **Dense table headers**: When a table has **4 or more columns** or tight vertical space, add `padding: 4px 8px` to every `<th>` to prevent header-row overflow.
    * **Overflow Prevention**: Calculate margins and image `max-height` carefully to ensure all elements (H2, images, tables, lists) fit perfectly within the vertical bounds.

4. **Flex List Items — Critical Text Wrapping Rule (Mandatory)**

    When a `<li>` uses `display: flex` (e.g., `display: flex; align-items: flex-start; gap: 12px;`), its direct children each become independent flex items. This means text nodes and `<span>` elements placed directly inside the `<li>` — after the icon or badge — are treated as **separate flex items**, causing them to be arranged horizontally and splitting Japanese text at the character level (e.g., `毎` / `月` / `以上` / `コンスタントに…` each on their own row).

    **Rule: Always wrap all text content after the icon/badge in a single `<span>`.**

    ```html
    <!-- WRONG — text node and inner <span> become separate flex items -->
    <li style="display: flex; align-items: flex-start; gap: 12px;">
      <i class="fa-solid fa-check-circle"></i>
      毎月<span class="accent">20GB以上</span>コンスタントに使う人
    </li>

    <!-- CORRECT — all text is one flex item; wraps naturally -->
    <li style="display: flex; align-items: flex-start; gap: 12px;">
      <i class="fa-solid fa-check-circle"></i>
      <span>毎月<span class="accent">20GB以上</span>コンスタントに使う人</span>
    </li>
    ```

    This rule applies even when the text has no inner `<span>` — wrap it anyway for consistency and future safety.

5. **Japanese Text Line Breaks**

    At font sizes of **46px or larger**, long Japanese strings will wrap at unnatural mid-phrase boundaries. Insert explicit `<br>` at semantically meaningful break points (after a particle like が/を/も, after punctuation, or between logical phrases).

    ```html
    <!-- Natural break after a meaningful chunk -->
    <span>毎月<span class="accent">20GB以上</span><br>コンスタントに使う人</span>
    <span>MNP/新規で最大<br><span class="accent-green">16,000PayPayポイント</span>還元</span>
    ```

    Aim for roughly equal visual line lengths. Do not break mid-word or in a way that separates a number from its unit.

    **Apply `<br>` in all contexts at 46px+**, including:
    * `terop-box` text — break at every ~20 characters or at logical phrase boundaries
    * `<td>` cells in tables — break at natural phrase boundaries when text exceeds ~15 characters
    * `<span>` inside list items — break before accent-colored sub-phrases when the combined line would be too long

    **Carrier/service name abbreviations**: Always use full names in slide text. Never abbreviate:
    * ❌ `SB` → ✅ `ソフトバンク`
    * ❌ `ドコモ系` when the full name fits → ✅ `ドコモ`
    * ❌ `楽天` (without `モバイル` when referring to the carrier) → ✅ `楽天モバイル`

6. **Image Selection & Asset Rules**
    * **No Placeholders**: Do NOT use `<Placeholder>` tags. Select and use the most appropriate existing image from `public/images/` (subdirectories: `common`, `irasutoya`, `logo`, `charts`, `temp`, `thumbnails`) based on the script context.
    * **Selection Priority (highest to lowest)**:
        1. **`public/images/temp/<carrier>/`**: Campaign banners, third-party reference screenshots, or any image that directly depicts the content being described. **Always prefer this over a generic logo or icon when a matching file exists.**
        2. **`public/images/slides/`**: Standard pre-made slides (see table below). Always use these for matching topics.
        3. **`public/images/thumbnails/`**: Related video CTA slides and デュアルSIM promotion slides (see rules 8 and 10 below).
        4. **`public/images/logo/`**: Service logos for carrier introduction slides.
        5. **`public/images/irasutoya/`**: Character illustrations for emotion/situation slides.
        6. **`public/images/common/`** or **`public/images/charts/`**: Conceptual diagrams and speed/price charts.
    * **Refer to `public/images/GEMINI.md`** for full file listings within each subdirectory.
    * **Image Styling**: Use `max-height: 500px; max-width: 100%; object-fit: contain;`. Apply `filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1))` for visibility.
    * **Full-Screen Images**: For charts or notice slides, use the `.fullscreen-img` class.
      `.fullscreen-img { width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; position: absolute; top: 0; left: 0; z-index: 10; }`
    * **Standard Slide Images (`public/images/slides/`)**: Several recurring slide types have dedicated pre-made images. **Always use these instead of generating custom HTML for these topics.**

      | File | Use when |
      |---|---|
      | `チャンネル登録と高評価よろしくお願いします.png` | Final CTA (チャンネル登録・高評価のお願い) |
      | `ブログもやってます.png` | Blog promotion slide |
      | `プランやキャンペーンは投稿時点のもの注意喚起.png` | Disclaimer — plans/campaigns as of recording date |
      | `今すぐ本編動画をチェック.png` | Promotion slide pointing to main video |
      | `毎月のスマホ代高すぎ.png` | Opening hook slide |
      | `評価は独断と偏見.png` | Disclaimer for evaluation slides |
      | `評価ランクの基準について.png` | Explanation of evaluation rank criteria |
      | `評価項目について.png` | Explanation of evaluation items |

    * **Thumbnails**: For CTA slides that are NOT covered by a standard slide image above, select the most relevant image from `public/images/thumbnails` based on file names.
    * **Captions/Citations**: Use small text (`font-size: 20px–35px`, color: `#666`) at the bottom of images if needed. Adjust image `max-height` to accommodate the text.

7. **Self-Check & Adjustment (Critical)**
    * **Overflow Check**: Before final generation, strictly verify that all content (text, images, tables) fits entirely within the `1280px × 720px` container.
    * **Maximize Space Usage**: Actively increase font sizes and image heights to fill available space. Aim for **less than 15% whitespace** within each slide. Start large, then scale down only if overflow occurs.
    * **Automatic Adjustment Rules**:
        * **Text**: If text is too long and overflows or overlaps, reduce the font size by 10%–20%.
        * **Images**: If images overlap with text or hit boundaries, reduce `max-height`/`max-width` and adjust margins.
        * **Tables**: If tables overflow, reduce cell font size down to a minimum of **30px**. If it still overflows, consider splitting the content into two slides.
    * **Whitespace**: Adjust `padding` or `gap` to ensure elements are not too close to the borders, but also maximize use of available space — do not leave large empty areas.

8. **"当チャンネル評価" (Radar Chart) Slides — Mandatory Rules**

    When generating a carrier/MVNO evaluation slide that shows a radar chart:

    * **Chart image only** — embed the chart using `height: 540px; object-fit: contain;` (use `height`, not `max-height`). Do **not** add a row of evaluation badges (`ss-badge`, `a-badge`, etc.) below the chart.
    * **Correct**:
      ```html
      <img src="public/images/charts/mineo.png" style="height: 540px; object-fit: contain; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1));" alt="mineoレーダーチャート">
      ```
    * **Wrong** (do not generate):
      ```html
      <img src="public/images/charts/mineo.png" style="max-height: 380px; max-width: 100%; ...">
      <div style="display: flex; gap: 16px; ...">
        <span class="ss-badge">料金 SS</span>
        ...
      </div>
      ```

9. **"過去動画" / Related Video CTA Slides — Thumbnail Requirement (Mandatory)**

    When a slide promotes a past video of the channel (e.g., "〇〇の過去動画もチェック！"), use the actual **thumbnail image** from `public/images/thumbnails/` — **never** a generic icon such as `fa-play-circle`.

    * Select the best-matching file from `public/images/thumbnails/` by partial keyword match on the carrier or topic name.
    * Embed at `max-height: 540px; object-fit: contain;`.

    ```html
    <!-- CORRECT -->
    <img src="public/images/thumbnails/【2026年最新】月額660円で実質使い放題！mineoの最強キャンペーンを徹底解説.png"
         style="max-height: 540px; object-fit: contain;" alt="mineo過去動画">
    <div class="terop-box" style="font-size: 54px;">
      mineoの<span style="color: var(--accent-yellow);">過去動画</span>もチェック！
    </div>

    <!-- WRONG — do not use a generic icon -->
    <i class="fa-solid fa-play-circle" style="font-size: 150px; color: var(--accent-red);"></i>
    ```

10. **Carrier Logo Sizing in Introduction / Detail Slides**

    In 2-column split slides where a carrier logo appears in the left `split-col` alongside a badge label below it:
    * Use a **fixed** `height: 80px` on the `<img>` (not `max-height: 140px; max-width: 380px`). This prevents the logo from dominating the column and ensures the badge label below it remains visible.

11. **Last Slide (CTA) — Thumbnail Requirement (Mandatory)**
    * The final slide **must** include the thumbnail image of the main (long-form) video that the short is promoting.
    * Determine the main video title from the `スライドに表示する内容` column of the last row in `台本.txt`.
    * Select the best-matching file from `public/images/thumbnails/` based on the title.
    * Embed the thumbnail using `<img src="public/images/thumbnails/[filename]" ...>`. Do **not** omit or use a placeholder.

12. **Output Format Requirements**
    * Output as a single HTML file containing all slides (div elements).
    * Use `body { display: flex; flex-direction: column; gap: 40px; }` to display all `.slide-container` elements vertically.
    * Add `<!-- Slide ID: XX -->` before each slide's HTML to map it to the script.

## Example of Special Common Slide
For slides that use a single fixed image, do not add text. Use the image only.

```html
<!-- Slide ID: XX -->
<div class="slide-container">
  <img src="public/images/slides/評価項目について.png" class="fullscreen-img">
</div>
```
