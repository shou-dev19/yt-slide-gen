Replace placeholder images in slide HTML files with actual image assets from the public/images directory.

Target HTML file: $ARGUMENTS (default: `slides.html`)

---

# Replace Slide Images Skill

This skill automates the process of replacing temporary or placeholder images (e.g., from `placehold.co`) in your slide HTML file with the correct local image assets located in `public/images/`.

## Workflow

1.  **Analyze Image Assets**:
    -   First, scan the `public/images/` directory and its subdirectories (`logo`, `irasutoya`, `common`, `slides`, `charts`, `temp`) to understand what images are available.
    -   Pay attention to filenames as they often describe the content (e.g., `docomo_logo.png`, `pose_anshin_woman.png`, `日本列島のイラスト.png`).

2.  **Analyze Slide HTML**:
    -   Read the target HTML file.
    -   Identify `<img>` tags that are using placeholder services (like `placehold.co`) or have `alt` attributes describing the desired image.
    -   Also look for existing images that might need to be updated to a better version if available.

3.  **Match and Replace**:
    -   For each identified image, find the best matching file in `public/images/`.
    -   **Logos**: Look in `public/images/logo/`. Keywords: "logo", company names (docomo, au, softbank, rakuten, aeon, mineo, etc.).
    -   **Illustrations/People**: Look in `public/images/irasutoya/`. Keywords: "woman", "man", "pose", "smartphone", emotions (relieved, happy, angry).
    -   **Common/Maps**: Look in `public/images/common/`. Keywords: "map", "japan", "sim", "smartphone".
    -   **Charts/Graphs**: Look in `public/images/charts/`. Keywords: "chart", "graph", "comparison".
    -   **Full Slide Images**: Look in `public/images/slides/`. These are often used when the entire slide content is pre-rendered as an image. Keywords: "title", "summary", "evaluation".
    -   **Temporary/Screenshots**: Look in `public/images/temp/` for specific screenshots like speed tests.

4.  **Update HTML**:
    -   Update the `src` attribute of the `<img>` tag to the relative path of the found image (e.g., `./images/logo/docomo_logo.png`).
    -   **Crucial**: Update or add `style` attributes to ensure the image fits well within the slide.
        -   **General Rule**: `object-fit: contain;` is almost always required.
        -   **Standard Size**: `max-width: 90%; max-height: 550px;` is a good starting point for main images.
        -   **Full Slide Replacements**: For slides that are just an image, use `width: 100%; height: 100%; object-fit: contain;`.
        -   **Icons/Logos**: Keep them smaller, e.g., `height: 60px;` or `max-height: 100px;` depending on context.

5.  **Verification**:
    -   Ensure the new `src` paths are correct relative to the HTML file location.
    -   Check that `alt` attributes are preserved or updated to reflect the new image.

## Example Usage

**Input HTML (Snippet):**
```html
<div class="slide-container">
    <h2>Communication Quality</h2>
    <img src="https://placehold.co/600x400?text=Speed+Test" alt="Speed Test Graph">
</div>
```

**Available Images:**
- `public/images/temp/speed_test_result.png`

**Action:**
- Identify "Speed Test Graph" matches `speed_test_result.png`.
- Replace `src` and add styling.

**Output HTML (Snippet):**
```html
<div class="slide-container">
    <h2>Communication Quality</h2>
    <img src="./images/temp/speed_test_result.png" style="max-width: 90%; max-height: 550px; object-fit: contain;" alt="Speed Test Graph">
</div>
```
