---
description: Generate HTML presentation slides from a script using the generate-html-slides skill
---

# /generate_html_slides

Use this workflow to automatically generate HTML presentation slides for YouTube videos based on a provided script (`台本.txt` or similar).

## Workflow Steps

1. **Understand the Requirements**: 
   - Review the script file provided by the user. If the user does not specify a file, default to checking `台本.txt`.
   - Take note of any specific instructions regarding theme colors (`--primary-color`, etc.), logo images, chart images, or common slides requested by the user.

2. **Invoke the Skill**: 
   - Read the `.gemini/skills/generate-html-slides/SKILL.md` rules and CSS template carefully.
   - Ensure you follow the "デカ文字" (Huge Text) design philosophy closely, maximizing visibility for smartphone viewers.

3. **Check for Assets**:
   - Check the `public/images/` directories (e.g. `public/images/charts`, `public/images/thumbnails`, `public/images/slides`, `public/images/irasutoya`, `public/images/logo`) to verify which visual assets requested by the script actually exist.

4. **Generate the Output**:
   - Create a single HTML file (e.g., `slides.html` unless specified otherwise by the user) containing all the consecutive slides detailed in the script.
   - For missing imagery, use the `<Placeholder>` tag with an appropriate prompt enclosed inside it, according to the `generate-html-slides` skill rules.

5. **Completion**:
   - Save the HTML file and present the result to the user.
