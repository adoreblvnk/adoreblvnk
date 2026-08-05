**Task Requirements & Strict Constraints:**

1. **Obsidian & Markdown Renderer Compatibility (CRITICAL):**
   * **DO NOT use `<defs>`, `<use>`, or `<symbol>` tags.** Markdown renderers like Obsidian aggressively sanitize SVGs for security and will completely strip these tags, causing the elements to disappear.
   * **Flatten all elements:** If a shape or icon repeats (like a computer, a server, or a node), you **must explicitly write the SVG code for each individual instance** at its specific `x` and `y` coordinates or using `transform="translate(x, y)"`. Do not reference reused components.
   * **No CSS `<style>` blocks:** Apply all styling directly to the elements using inline presentation attributes (e.g., `fill="#ffffff" stroke="#000000" stroke-width="2"`).

2. **Searchable Text:**
   * All text in the diagram MUST be rendered using the SVG `<text>` tag. 
   * **DO NOT** convert text into vector paths. The text must remain selectable and searchable.
   * Use standard, widely available system fonts (e.g., `font-family="Arial, Helvetica, sans-serif"`).
   * Ensure text alignment is accurate using `text-anchor` (e.g., `start`, `middle`, `end`) and proper `x` and `y` coordinates.

3. **Accuracy and Layout:**
   * Match the colors, stroke widths, border radiuses (`rx`, `ry`), and overall proportions as accurately as possible to the source image.
   * Ensure the SVG is responsive. Define a proper `viewBox` (e.g., `viewBox="0 0 1000 800"`) and set `width="100%"` and `height="100%"`.
   * Add a solid background rectangle (e.g., `<rect width="100%" height="100%" fill="#ffffff" />`) if the diagram relies on a white background, to ensure it remains legible in dark mode.

4. **Code Structure:**
   * Organize the code logically using group tags with descriptive IDs (e.g., `<g id="web-server">`, `<g id="connections">`, `<g id="labels">`).
   * Layer the SVG correctly (e.g., draw connection lines first, then shapes, then text on top).

**Output format:**
Output **ONLY** the raw SVG code (not inside any code block). Do not include any explanations, apologies, or conversational text.

