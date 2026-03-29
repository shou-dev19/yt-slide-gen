---
description: Generate HTML presentation slides for YouTube shorts based on a script, applying an ultra-bold, high-impact design suitable for smartphone viewing.
---

# Generate YouTube Shorts Slides Workflow

Use this workflow to generate high-impact, 1:1 aspect ratio HTML slides from a given script file (e.g., `台本.txt`).

1. **Analyze Script**: Use the `view_file` tool to read the script entirely. Identify the number of slides, the speaker dialogue, visual instructions, and the core message required for each slide. Extract extremely short and impactful phrases for headers.
2. **Read Skill**: Ensure you've read `.agent/skills/generate-short-slides/SKILL.md` for specific formatting instructions entirely.
3. **Generate HTML**: Use `write_to_file` to output the base `slides-short.html`. Follow the specific layout rules, typography (`Inter`, `Noto Sans JP` ultra-bold), and the required color theme (Blue/White/Red) defined in the skill. Be sure to establish CSS classes to support Image Placeholders and dynamic typography.
4. **Placeholder Replacement**: Notify the user that the base HTML has been created with temporary text/emoji placeholders. Invite the user to provide the exact paths to specific image assets (e.g. logos, characters, graphs, thumbnails).
5. **Asset Insertion**: As the user provides image file paths, utilize the `replace_file_content` tool to perfectly substitute the placeholder `<div>` or explicit text with well-formatted `<img>` tags utilizing CSS adjustments (`drop-shadow`, `object-fit: contain`, etc) to perfectly align with the surrounding styles. Iterate until the user is satisfied.
