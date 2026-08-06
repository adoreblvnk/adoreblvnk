# AGENTS.md

## General principles
<!-- https://x.com/MarcosHernanz/status/2083954734487212511 -->
- Do not preserve backward compatibility. Remove obsolete paths instead of adding compatibility layers, fallbacks, or migrations.
- Choose the simplest implementation that fully meets the current requirements. Avoid speculative abstractions, configuration, and indirection.
- Grow the system in layers. Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
- Keep components modular and concerns clearly separated.
- Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability. Do not reimplement common functionality without a clear reason.
- Lean on the dependencies already in the project before writing your own implementation or adding packages. Do not assume a library lacks a capability without checking its documentation and types.
- Make architectural decisions for the long term. Do not accept a stopgap that only works for now and is meant to be replaced later.
- Study how established products solve the problem before designing a solution. Adopt their proven patterns and conventions rather than inventing an approach from scratch.

## Project conventions

- When adapting official documentation or an established implementation, preserve its structure and line order where practical. Make the smallest project-required diff, keep local terminology, cite the source, and explain only non-obvious deviations.
- Use a power-of-two-derived scale. A value may be a power of two (`2, 4, 8, 16, 32, ...`) or that power plus exactly one of its three immediately preceding powers. For example, from `32`, permit `36` (`32 + 4`), `40` (`32 + 8`), and `48` (`32 + 16`), but reject `34` (`32 + 2`). Apply the scale to project-authored interface geometry:
  - Spacing.
  - Border radii.
  - Interface element dimensions.
  - Other project-authored spatial values where consistency matters.
  - Use judgement for optical, intrinsic, or dependency-owned values; `1px` hairlines remain valid.
