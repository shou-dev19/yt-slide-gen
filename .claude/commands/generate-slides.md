Generate a React component for slides based on a script file, using placeholders for images.

Script file path: $ARGUMENTS (default: `台本.txt`)

---

# Generate Slides (Structure Only)

This skill generates a React component (`GeneratedSlidesViewer.tsx`) that renders the layout and text of slides for a YouTube video based on a script (`台本.txt`). It **does not** generate images. Instead, it places `<Placeholder>` components where images should go.

## Input

*   **Script File:** Path to the script file (default: `台本.txt`).

## Output

*   **Target File:** `src/generated/GeneratedSlidesViewer.tsx`

## Process

1.  **Analyze Brand/Theme:**
    *   Read the script to identify the main subject.
    *   Select appropriate theme colors (`--primary-color`, etc.) for UQ Mobile, Ahamo, Rakuten, etc.

2.  **Generate Component Structure:**
    *   Construct the slide logic using the **Template Code** below.
    *   **Text content:** Populate `h1`, `h2`, `p`, lists normally.
    *   **Image placeholders:**
        *   **CRITICAL:** When the script describes a visual scene (e.g., "confused face", "user holding phone"), **DO NOT GENERATE AN IMAGE**.
        *   Instead, insert a `<Placeholder>` component.
        *   **Format:** `<Placeholder text="[IMAGE_PROMPT] Description of the image to generate later" height="400px" />`
        *   The `text` prop MUST start with `[IMAGE_PROMPT]` so the next agent knows it needs generation.
    *   **Existing Assets:**
        *   For **Charts**, use `<ImageBox src="charts/images/filename.png" />` if the file exists. Maximize size by setting width to 100% and removing headers if needed.
        *   For **Thumbnails**, use `<ImageBox src="thumbnails/filename.png" />` if the file exists.
        *   If not sure, use `<Placeholder text="[EXISTING_ASSET] Check for chart/thumbnail" />`.
    *   **Common Slides (IMPORTANT):**
        *   Use static images for standard segments instead of generating text/placeholders.
        *   **Evaluation Items:** `slides/common/評価項目について.png`
        *   **Rank Criteria:** `slides/common/評価ランクの基準について.png`
        *   **Disclaimer (Opinion):** `slides/common/評価は独断と偏見.png`
        *   **Disclaimer (Date/Campaign):** `slides/common/プランやキャンペーンは投稿時点のもの注意喚起.png`
        *   **Blog Promo:** `slides/common/ブログもやってます.png`
        *   **Subscribe/Like:** `slides/common/チャンネル登録と高評価よろしくお願いします.png`
        *   *Implementation:* Use `<Slide id="..." className="image-only-slide"><Img src={staticFile("slides/common/FILENAME.png")} ... /></Slide>`

3.  **Refine Design/Layout:**
    *   **Dense Text:** If a slide has extensive text or lists (e.g., 5+ items), add `className="text-large"` to the `<Slide>` component to increase font size.
    *   **Charts:** When showing a chart, remove the `<h2>` title if it allows the chart to be significantly larger.
    *   **Slide IDs:** Do NOT render slide IDs visibly on the slide.

## Design Rules

*   **Resolution:** 1280x720.
*   **Font:** 'M PLUS Rounded 1c' (Weight: 800/900).
*   **Color Palette:** Set via CSS variables based on the carrier brand.

## Template Code

```tsx
import React from 'react';

// --- CSS Styles ---
// Update based on brand!
const cssStyles = `
  @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@800;900&display=swap');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

  :root {
    --primary-color: #E6007F; /* REPLACE */
    --secondary-color: #3366CC; /* REPLACE */
    --accent-yellow: #ffca28;
    --accent-red: #ff3d00;
    --text-dark: #1a237e;
    --bg-white: #ffffff;
  }
  
   * { box-sizing: border-box; }
  .slide-container { width: 1280px; height: 720px; background: var(--bg-white); border: 10px solid var(--primary-color); padding: 40px; font-family: 'M PLUS Rounded 1c'; color: var(--text-dark); display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; overflow: hidden; flex-shrink: 0; }
  h1 { font-size: 130px; font-weight: 900; margin: 0; line-height: 1.1; text-shadow: 3px 3px 0 white, 6px 6px 0 var(--primary-color); text-align: center; }
  h2 { font-size: 90px; font-weight: 800; margin: 0 0 30px 0; border-bottom: 8px solid var(--accent-yellow); display: inline-block; padding-bottom: 10px; text-align: center; }
  p, li { font-size: 64px; font-weight: 800; line-height: 1.4; margin: 20px 0; }
  ul { list-style: none; padding: 0; }
  li::before { content: '✅'; margin-right: 20px; }
  strong, .highlight { color: var(--accent-red); }
  .accent-text { color: var(--primary-color); }

  .text-large p, .text-large li { font-size: 80px; }
  .image-only-slide { border: none !important; padding: 0 !important; background: transparent !important; }

  .split-layout { display: flex; width: 100%; height: 100%; align-items: center; justify-content: space-around; }
  .split-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
  
  .img-placeholder { background-color: #ffeb3b; border: 5px dashed #f57f17; display: flex; justify-content: center; align-items: center; color: #333; font-size: 30px; margin: 20px; text-align: center; padding: 20px; opacity: 0.8; }
  
  .chapter-slide { background-color: var(--primary-color); border: none !important; color: white !important; }
  .chapter-slide h2 { color: #FFD700 !important; border-bottom: none !important; }
  .chapter-slide h1 { color: white !important; text-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important; }
  .chapter-line { width: 80%; height: 10px; background: white; border-radius: 5px; margin-top: 20px; }
`;

const Slide = ({ id, children, className = '' }: { id: string, children: React.ReactNode, className?: string }) => (
    <div id={id} className={`slide-container ${className}`}>
        {children}
    </div>
);

const Placeholder = ({ text, width = '100%', height = '300px' }: { text: string, width?: string, height?: string }) => (
    <div className="img-placeholder" style={{ width, height }}>
        <i className="fa-solid fa-wand-magic-sparkles" style={{ marginRight: '15px' }}></i>
        {text}
    </div>
);

const Icon = ({ name, color, size = '150px' }: { name: string, color?: string, size?: string }) => (
    <i className={`fa-solid fa-${name}`} style={{ fontSize: size, color: color || 'var(--text-dark)', margin: '20px' }}></i>
);

const ImageBox = ({ src, width = '400px', height = 'auto' }: { src: string, width?: string, height?: string }) => (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '20px', width, height }}>
        <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
    </div>
);

const SlidesContent = () => {
    return (
        <>
            <style>{cssStyles}</style>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '50px', background: '#333', padding: '50px', alignItems: 'center' }}>
                {/* Generated Content Here */}
            </div>
        </>
    );
};

export const GeneratedSlidesViewer = () => {
    return (
        <AbsoluteFill style={{ overflowY: 'auto', backgroundColor: '#333' }}>
            <SlidesContent />
        </AbsoluteFill>
    );
};
```
