---
name: adore_blvnk
description: An achromatic identity surface built around animated 3D form rendered as dithered machine vision.
colors:
  carbon-ink: "oklch(0.08 0 0)"
  cold-paper: "oklch(0.95 0.004 210)"
  signal-white: "oklch(0.98 0.002 210)"
  link-blue: "oklch(0.62 0.08 240)"
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
  writing-index-heading:
    fontFamily: "Lexend, sans-serif"
    fontSize: "32px"
    fontWeight: 400
    lineHeight: "48px"
    letterSpacing: "-0.02em"
  writing-article-heading:
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
  writing-link:
    textColor: "{colors.link-blue}"
    underline: "1px on hover and focus"
---

# Design System: adore_blvnk

## 1. Overview

**Creative North Star: "The Registered Position"**

The interface is an achromatic registration field built around animated 3D form rendered as dithered machine vision. Its defining aesthetic lives in the asset: a solid GLB oscillates between scan, halftone, and digital noise while remaining legible in motion. Coordinate trackers, registration corners, and a measured lattice frame that presence as deliberate evidence.

The composition is sparse but active. Large Lexend statements supply mass; Space Mono carries controls, coordinates, and routes. Full-viewport movement, hard alignments, and decisive inversion create controlled intensity while keeping the asset dominant.

**Key Characteristics:**
- Monochrome section inversion with no ornamental accent color; cold blue is reserved for functional prose links.
- One animated, dithered 3D form as the identity-bearing visual anchor.
- Square geometry, hairline registration marks, and flat controls.
- Display mass from Lexend; operational detail from Space Mono.
- Technical overlays and motion that register identity, pose, position, or interaction.

## 2. Colors

A cold achromatic palette gives the animated form, type, and spatial instrumentation one severe visual register.

### Primary
- **Carbon Ink:** The default field and primary text on paper sections.
- **Cold Paper:** The principal foreground and inverted section field, with a slight blue cast that distinguishes it from pure white.

### Secondary
- **Signal White:** High-contrast type placed over difference-blended scene content and the brighter reading value for identity-bearing text.
- **Link Blue:** A restrained cold blue reserved for inline prose links. It identifies links at rest; hover and focus add a one-pixel underline.

### Neutral
- **Dark Registration:** Hairlines and registration marks over Carbon Ink.
- **Light Registration:** Hairlines and registration marks over Cold Paper.

### Named Rules

**The Signal-Only Rule.** Color is structural: field, foreground, border, scene signal, or functional prose-link identification. Emphasis comes from inversion, weight, scale, and motion.

**The Inversion Rule.** Section transitions exchange Carbon Ink and Cold Paper while preserving the legibility of the animated asset and contact routes.

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
- **Body** (400, 17px, 1.8 line-height): Long-form writings, capped by the 768px reading measure.
- **Writing Index Heading** (400, 32px, 48px line-height): The writings index title.
- **Writing Article Heading** (400, 40px, 48px line-height): Individual writing titles.
- **Label** (400–700, 14px, up to 0.12em tracking): Navigation, contact prefixes, and controls. Uppercase is reserved for terse operational labels.
- **Meta** (400, 11px, 16px line-height): Dates, summaries, tags, and secondary writing metadata.
- **HUD** (400, 9px, 1 line-height): Coordinate trackers and spatial evidence only.

### Named Rules

**The Mass-and-Measure Rule.** Lexend carries identity and prose; Space Mono measures, labels, routes, and controls.

**The Tracking Floor Rule.** Display letter-spacing never tightens beyond -0.04em. If a word collides or overflows, reduce scale before tightening type.

## 4. Elevation

The system is flat. Depth comes from the WebGL figure, section inversion, opacity, difference blending, masks, and fixed layer order. One-pixel borders establish structure without simulating elevation.

### Named Rules

**The Evidence Layer Rule.** HUD marks and trackers reinforce identity, pose, position, focus, or interaction.

## 5. Components

Components are square, terse, and mechanically responsive. Their states use inversion and measured displacement.

### Buttons
- **Shape:** Square control geometry (0 radius), 48px high, with 16px horizontal padding and a one-pixel foreground border.
- **Primary:** Transparent field with current foreground text in Space Mono at 14px.
- **Hover / Focus:** Hover inverts field and text. Focus uses a two-pixel current-foreground outline offset by 4px. Active state compresses to 96% scale using the fast exponential transition.

### Chips
- **Style:** Writing tags use square one-pixel translucent Cold Paper borders, 4px × 8px padding, and 11px uppercase Space Mono.
- **State:** Tags are informational and remain square.

### Cards / Containers
- **Corner Style:** Square containers aligned to the registration geometry.
- **Background:** Containers inherit Carbon Ink or Cold Paper from their section.
- **Shadow Strategy:** Depth comes from contrast, overlap, and scene layers.
- **Border:** One-pixel dividers only where they establish list or reading structure.
- **Internal Padding:** 16px or 24px according to density.

### Navigation

The fixed 80px masthead pairs a 900-weight Lexend identity mark with a 700-weight Space Mono writings route. Both links provide a 48px minimum target. Desktop navigation uses difference blending; mobile navigation resolves to the current section colors with a one-pixel bottom divider.

### Contact Index

Contact routes are unboxed rows separated by one-pixel registration lines. Each row pairs a 14px operational prefix with a 17px address, uses 24px vertical padding, and shifts 16px to the right on hover. Mobile stacks prefix and address with a compact 6px gap to protect long addresses.

### Writing Index

Writing entries use a 96px date column and a flexible title column, separated by 24px. The pattern collapses to one column below 600px. Titles carry 700 weight; dates and summaries stay quieter without sacrificing readable contrast.

### Prose Links

Inline writing links use Link Blue without an underline at rest. Hover and keyboard focus add a one-pixel current-color underline with a 6px optical offset. Navigation, contact rows, writing-index rows, and buttons keep their structural affordances instead of adopting the prose-link treatment.

## 6. Do's and Don'ts

### Do:
- **Do** keep the animated, dithered GLB as the single identity-bearing visual anchor.
- **Do** preserve anatomy, pose, and hand sign through every dither, camera, and interaction treatment.
- **Do** use the 8/12/16/24/32/48/64/80/96/128px spatial vocabulary, with 4px reserved for optical insets and 6px for compact internal gaps.
- **Do** keep contact routes and the identity phrase readable during theme inversion and WebGL context recovery.
- **Do** tie technical overlays to identity evidence: pose, position, registration, pointer focus, or interaction.
- **Do** provide reduced-motion behavior for entrance, section, and interaction animation.

### Don't:
- **Don't** turn the interface into a generic SaaS landing page, soft glass card system, or warm editorial template.
- **Don't** let specimen-style UI chrome, excessive telemetry, barcodes, fictional operating-system chrome, or status readouts compete with the animated asset.
- **Don't** make the 3D character cute or mascot-like, coat it in glossy cyber-armor, or surround it with decorative point clouds.
- **Don't** let interaction sacrifice the character's pose or hand sign.
- **Don't** add gradients, ornamental accent colors, soft shadows, rounded card grids, or pill-shaped informational tags.
- **Don't** use monospace as blanket technical shorthand or repeat tiny uppercase eyebrows as section scaffolding.
