---
description: Generate HTML presentation slides for YouTube shorts based on a script, applying an ultra-bold, high-impact design suitable for smartphone viewing.
---

# Generate YouTube Shorts Slides Workflow

Use this workflow to generate high-impact, 1:1 aspect ratio HTML slides from a given script file (e.g., `台本.txt`).

1. **Analyze Script**: 
   - Use the `view_file` tool to read the script entirely. 
   - Identify the number of slides, visual instructions, and core message for each slide. 
   - Extract extremely short and impactful phrases for headers.

2. **Select Assets**:
   - Refer to `public/images/GEMINI.md` to identify appropriate images (logos, concept illustrations, emotional icons, charts) for each slide.
   - Choose the best matching assets from `public/images/`.

3. **Read Skill**: 
   - Read `.gemini/skills/generate-short-slides/SKILL.md` for specific formatting instructions.

4. **Generate HTML**: 
   - Create `slides-short.html`.
   - Follow the layout rules, typography (`Inter`, `Noto Sans JP` ultra-bold), and the required color theme (Blue/White/Red).
   - Insert selected `<img>` tags directly into the HTML with styling (`drop-shadow`, `object-fit: contain`).
   - Do NOT use placeholders.

5. **Completion**:
   - Save the HTML file and present the result to the user.
