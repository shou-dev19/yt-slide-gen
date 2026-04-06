---
name: generate-html-slides
description: Generate a presentation slides HTML file based on a script, applying a 'Huge Text' design, specific colors, and image asset mapping.
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
    * **Tables**: Base font size **50px**. Ensure rows do not overflow the 720px height. Adjust padding and font size meticulously if there are many rows.
    * **Overflow Prevention**: Calculate margins and image `max-height` carefully to ensure all elements (H2, images, tables, lists) fit perfectly within the vertical bounds.

4. **Image Selection & Asset Rules**
    * **No Placeholders**: Do NOT use `<Placeholder>` tags. Select and use the most appropriate existing image from `public/images/` (subdirectories: `common`, `irasutoya`, `logo`, `charts`) based on the script context.
    * **Selection Logic**: Refer to `public/images/GEMINI.md` for mapping:
        * **Logos**: Use `public/images/logo/` for service mentions (ahamo, LINEMO, etc.).
        * **Concepts**: Use `public/images/common/` for conceptual explanations (e.g., congestion, road metaphors).
        * **Emotions/Situations**: Use `public/images/irasutoya/` for reactions (e.g., shock, joy, saving money).
        * **Charts**: Use `public/images/charts/` or `common/` for price tables and speed comparisons.
    * **Image Styling**: Use `max-height: 500px; max-width: 100%; object-fit: contain;`. Apply `filter: drop-shadow(0 10px 20px rgba(0,0,0,0.1))` for visibility.
    * **Full-Screen Images**: For charts or notice slides, use the `.fullscreen-img` class.
      `.fullscreen-img { width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; position: absolute; top: 0; left: 0; z-index: 10; }`
    * **Thumbnails**: For CTA slides, select the most relevant image from `public/images/thumbnails` based on file names.
    * **Captions/Citations**: Use small text (`font-size: 20px–35px`, color: `#666`) at the bottom of images if needed. Adjust image `max-height` to accommodate the text.

5. **Self-Check & Adjustment (Critical)**
    * **Overflow Check**: Before final generation, strictly verify that all content (text, images, tables) fits entirely within the `1280px × 720px` container.
    * **Automatic Adjustment Rules**:
        * **Text**: If text is too long and overflows or overlaps, reduce the font size by 10%–20%.
        * **Images**: If images overlap with text or hit boundaries, reduce `max-height`/`max-width` and adjust margins.
        * **Tables**: If tables overflow, reduce cell font size down to a minimum of **30px**. If it still overflows, consider splitting the content into two slides.
    * **Whitespace**: Adjust `padding` or `gap` to ensure elements are not too close to the borders.

6. **Output Format Requirements**
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
