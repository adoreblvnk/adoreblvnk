---
name: adore_blvnk
description: Achromatic instrumented minimalism theme with dithered machine vision, and computational brutalism for transitions & animation.
colors:
  carbon-ink: "oklch(0.08 0 0)"
  cold-paper: "oklch(0.95 0.004 210)"
  signal-white: "oklch(0.98 0.002 210)"
  link-blue: "#89B4FA"
  dark-registration: "oklch(0.55 0 0)"
  light-registration: "oklch(0.45 0.003 210)"
typography:
  mega:
    fontFamily: "Lexend, sans-serif"
    fontSize: "clamp(64px, 10vw, 144px)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-0.04em"
  display:
    fontFamily: "Lexend, sans-serif"
    fontSize: "clamp(42px, 8vw, 88px)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Lexend, sans-serif"
    fontSize: "clamp(32px, 8vw, 96px)"
    fontWeight: 900
    lineHeight: 0.85
    letterSpacing: "-0.04em"
  title:
    fontFamily: "Lexend, sans-serif"
    fontSize: "21px"
    fontWeight: 900
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Lexend, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.8
    letterSpacing: "-0.01em"
  position-bio:
    fontFamily: "Space Mono, monospace"
    fontSize: "clamp(17px, 1.35vw, 22px)"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "-0.025em"
    measure: "36ch"
  body-strong:
    fontFamily: "Lexend, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.8
  writing-entry-title:
    fontFamily: "Lexend, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.5
  writing-page-heading:
    fontFamily: "Lexend, sans-serif"
    fontSize: "40px"
    fontWeight: 400
    lineHeight: "48px"
    letterSpacing: "-0.02em"
  label:
    fontFamily: "Space Mono, monospace"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.08em"
  meta:
    fontFamily: "Space Mono, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: "16px"
  hud:
    fontFamily: "Space Mono, monospace"
    fontSize: "9px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.06em"
rounded:
  none: "0"
  control: "2px"
spacing:
  optical: "4px"
  compact: "6px"
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
  4xl: "80px"
  5xl: "96px"
  6xl: "128px"
components:
  action-button:
    backgroundColor: "transparent"
    textColor: "{colors.cold-paper}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0 16px"
    height: "48px"
  action-button-hover:
    backgroundColor: "{colors.cold-paper}"
    textColor: "{colors.carbon-ink}"
  navigation-link:
    backgroundColor: "transparent"
    textColor: "{colors.cold-paper}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    height: "48px"
  writing-tag:
    backgroundColor: "transparent"
    textColor: "{colors.signal-white}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "4px 8px"
  article-link:
    textColor: "{colors.link-blue}"
    underline: "1px on hover and focus"
---

# Design System: adore_blvnk

## 1. Overview

**Creative North Star: "Instrumented Minimalism"**

The interface is an achromatic identity field built around one animated 3D figure, restrained typography, and spatial instrumentation. Dithered machine vision is its material language. Coordinate trackers, registration corners, and a measured lattice frame the figure as deliberate evidence without competing with it.

Computational brutalism governs transitions and animation. Scan states, digital noise, hard inversion, fragmentation, and forceful movement create controlled intensity between sparse, functional compositions. Large Lexend statements supply mass; Space Mono carries controls, coordinates, and routes.

**Key Characteristics:**
- Monochrome section inversion with no ornamental accent color; Link Blue is reserved for functional prose links.
- One animated, dithered 3D figure as the identity-bearing visual anchor.
- Square geometry, hairline registration marks, and flat controls.
- Display mass from Lexend; operational detail from Space Mono.
- Technical overlays and motion that register identity, pose, position, or interaction.
- Shared content lines govern every composition. The position bio's right edge mirrors the primary left content inset.

## 2. Colors

A cold achromatic palette unifies the 3D figure, type, and spatial instrumentation without adding ornamental emphasis.

### Primary
- **Carbon Ink:** The default field and primary text on paper sections.
- **Cold Paper:** The principal foreground and inverted section field, with a slight blue cast that distinguishes it from pure white.

### Secondary
- **Signal White:** High-contrast type placed over difference-blended scene content and the brighter reading value for identity-bearing text.
- **Link Blue:** Sourced from Catppuccin Mocha Blue and reserved for inline prose links. It identifies links at rest; hover and focus add a one-pixel underline.

### Neutral
- **Dark Registration:** Hairlines and registration marks over Carbon Ink.
- **Light Registration:** Hairlines and registration marks over Cold Paper.

### Named Rules

**The Signal-Only Rule.** Color is structural: field, foreground, border, scene signal, or functional prose-link identification. Emphasis comes from inversion, weight, scale, and motion.

**The Inversion Rule.** Section transitions exchange Carbon Ink and Cold Paper while preserving the legibility of the 3D figure and contact routes.

**The Alpha Hierarchy Rule.** Transparency subordinates borders, metadata, inactive kinetic type, and HUD evidence without creating new color roles.

## 3. Typography

**Display Font:** Lexend

**Body Font:** Lexend

**Label/Mono Font:** Space Mono

**Character:** Lexend gives identity statements dense geometric authority while remaining legible through dither and motion. Space Mono makes navigation, metadata, contact routes, code, and tracking read as operational evidence.

### Hierarchy
- **Mega** (900, fluid 64–144px, 1 line-height): Low-opacity ghost type behind the hero.
- **Display** (900, fluid 42–88px, 1 line-height): The identity name; balance lines and never exceed the established -0.04em tracking floor.
- **Headline** (900, fluid 32–96px, 0.85 line-height): Kinetic all-caps statements and colophon-scale type only.
- **Title** (900, 21px, 1.05 line-height): Short identity phrases and compact section-level statements.
- **Body** (400, 17px, 1.8 line-height): Long-form article prose, capped by the 768px reading measure.
- **Position Bio** (400, fluid 17–22px, 1.55 line-height): A 36ch Space Mono identity note that may cross the figure while preserving its mirrored right alignment.
- **Body Strong** (600, 17px, 1.8 line-height): Prose emphasis without approaching display weight.
- **Writing Entry Title** (700, 17px, 1.5 line-height): Titles in the Writings index.
- **Writing Page Heading** (400, 40px, 48px line-height): The Writings index title and article titles.
- **Label** (400–700, 14px, up to 0.12em tracking): Navigation, contact prefixes, and controls. Uppercase is reserved for terse operational labels.
- **Meta** (400, 11px, 16px line-height): Writing-index dates and summaries, tags, and secondary metadata.
- **HUD** (400, 9px, 1 line-height): Coordinate trackers and spatial evidence only.

### Named Rules

**The Mass-and-Measure Rule.** Lexend carries identity and prose; Space Mono measures, labels, routes, and controls.

**The Tracking Floor Rule.** Display letter-spacing never tightens beyond -0.04em. If a word collides or overflows, reduce scale before tightening type.

## 4. Elevation

The system is flat. Depth comes from the 3D figure, opacity, difference blending, masks, section inversion, and fixed layer order. One-pixel borders establish structure without simulating elevation.

### Named Rules

**The Evidence Layer Rule.** HUD marks and trackers reinforce identity, pose, position, focus, or interaction.

## 5. Components

Components are square, terse, and mechanically responsive. Their states use inversion and measured displacement.

### Buttons
- **Shape:** Square, flat, and bordered.
- **States:** Hover inverts field and text, focus remains visibly outlined, and active states compress briefly.

### Writing Tags
- **Style:** Writing Tags are square, translucent, uppercase metadata rather than interactive controls.

### Cards / Containers
- **Corner Style:** Square containers aligned to the registration geometry.
- **Background:** Containers inherit Carbon Ink or Cold Paper from their section.
- **Shadow Strategy:** Depth comes from contrast, overlap, and scene layers.
- **Border:** One-pixel dividers only where they establish list or reading structure.
- **Internal Padding:** 16px or 24px according to density.

### Navigation

The fixed, transparent masthead uses difference blending at every viewport size. Mobile narrows its horizontal inset without changing its visual treatment.

### Contact Index

Contact routes are unboxed rows separated by registration lines. Each row pairs an operational prefix with an address; mobile stacks them to protect long addresses.

### Position Composition

The position section pairs low-opacity kinetic Lexend type with a right-aligned Space Mono biography. The figure sits left of center and may pass behind the biography. The biography preserves the shared mirrored margin instead of following the section's smaller right padding. On narrow screens, the figure scales down and shifts up and left while the biography stacks below the kinetic type without overlap.

### Writing Index

Writing entries align dates and content in two columns, then collapse to one column on narrow screens. Dividers establish list rhythm while dates and summaries remain subordinate to titles.

### Article

Article headers use ISO 8601 publication dates and the shared Writing Tag treatment. Metadata wraps when space is constrained.

### Prose Links

Inline article links use Link Blue without an underline at rest and underline on hover or keyboard focus. Code blocks use the Vesper syntax theme. Navigation, contact rows, Writing Entries, and buttons retain their structural affordances.

## 6. Do's and Don'ts

### Do:
- **Do** keep the animated, dithered figure as the single identity-bearing visual anchor.
- **Do** preserve anatomy, pose, and hand sign through every dither, camera, and interaction treatment.
- **Do** use the 8/12/16/24/32/48/64/80/96/128px spatial vocabulary, with 4px reserved for optical insets and 6px for compact internal gaps.
- **Do** keep contact routes and the identity phrase readable during theme inversion.
- **Do** preserve shared alignment lines and mirrored outer margins when copy, asset placement, or viewport size changes.
- **Do** tie technical overlays to identity evidence: pose, position, registration, pointer focus, or interaction.
- **Do** provide reduced-motion behavior for entrance, section, and interaction animation.

### Don't:
- **Don't** turn the interface into a generic SaaS landing page, soft glass card system, or warm editorial template.
- **Don't** let specimen-style UI chrome, excessive telemetry, barcodes, fictional operating-system chrome, or status readouts compete with the 3D figure.
- **Don't** make the 3D character cute or mascot-like, coat it in glossy cyber-armor, or surround it with decorative point clouds.
- **Don't** let interaction sacrifice the character's pose or hand sign.
- **Don't** add gradients, ornamental accent colors, soft shadows, rounded card grids, or pill-shaped informational tags.
- **Don't** use monospace as blanket technical shorthand or repeat tiny uppercase eyebrows as section scaffolding.
