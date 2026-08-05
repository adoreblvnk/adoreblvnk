Convert the PDF/slides into Markdown. When the source contains diagrams, embed them as SVG in the Markdown.

For each diagram:
- Reproduce what the source diagram conveys; do not create an enriched teaching diagram.
- Priority: meaning/relationships > text visibility > label placement > node placement > style/color.
- Render or inspect the source page/image first; diagram geometry comes from the visual source, not extracted text order.
- Inventory visible boundaries, nodes, connections, labels, arrows, axes, legends, hierarchy, grouping, and other meaning-bearing marks.
- Do not add labels, values, notes, callouts, relationships, or facts from surrounding text unless they are visible in the diagram or explicitly requested.
- Use simple SVG primitives and readable text; avoid decorative styling that reduces clarity or forces label movement.
- Place labels beside the same object/edge/region as the source, avoiding overlaps and ambiguous attachment.
- Render the generated SVG and visually compare against the source; fix missing, misplaced, unreadable, or extra content before finalizing.

