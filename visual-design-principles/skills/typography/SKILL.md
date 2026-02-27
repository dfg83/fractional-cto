---
name: typography
description: This skill should be used when the user is selecting typefaces, defining font sizes, creating typographic scales, pairing fonts, setting line height or line length, building heading hierarchies, configuring web fonts, or implementing responsive typography. Covers modular type scales (Major Third, Perfect Fourth), the 2-3 font family limit, Bringhurst's line length rule (45-75 characters), and micro-typography.
version: 1.0.0
---

# Typography Is the Foundation — Get It Right and Everything Else Follows

Typography accounts for 95% of web design (Oliver Reichenstein, iA). A correct type system makes every page look intentional. A broken one makes every page look amateur — regardless of color, imagery, or layout.

## The 2-3 Font Family Maximum

Limit every project to **2-3 font families maximum.** More than three creates visual noise and increases page weight.

**Pairing strategy — contrast, not similarity:**

| Pairing Type | Heading | Body | Example |
|-------------|---------|------|---------|
| Serif + Sans-serif | Playfair Display | Inter | Editorial, marketing |
| Geometric + Humanist | Poppins | Source Sans Pro | SaaS, dashboards |
| Monospace + Sans-serif | JetBrains Mono | Inter | Developer tools |
| Single family | Inter (bold) | Inter (regular) | Minimal, utilitarian |

The single-family approach (one typeface, varied weights) is the safest choice for applications. It guarantees harmony and reduces load time.

## Modular Type Scale

Define font sizes using a mathematical ratio, not arbitrary values. Multiply the base size by the ratio for each step.

**Base size: 16px (1rem).** Never go below 16px for body text on screens.

| Scale Name | Ratio | Sizes from 16px base |
|-----------|-------|----------------------|
| **Minor Third** | 1.200 | 16 / 19.2 / 23.0 / 27.6 / 33.2 |
| **Major Third** | 1.250 | 16 / 20 / 25 / 31.3 / 39.1 |
| **Perfect Fourth** | 1.333 | 16 / 21.3 / 28.4 / 37.9 / 50.5 |
| **Golden Ratio** | 1.618 | 16 / 25.9 / 41.9 / 67.8 / — |

**Selection guide:** Use Minor Third for dense UIs (dashboards, admin panels). Use Major Third or Perfect Fourth for content-heavy pages. Use Golden Ratio sparingly — only for dramatic editorial layouts.

## Line Height Rules

| Context | Line Height | Reason |
|---------|-------------|--------|
| **Body text** | 1.4–1.6 | Optimal readability per Bringhurst |
| **Headings** | 1.1–1.3 | Tighter to maintain visual weight |
| **ALL CAPS text** | 1.0–1.2 | Caps are uniform height; needs less leading |
| **Small/caption text** | 1.5–1.7 | Smaller text needs proportionally more space |

Add `letter-spacing: 0.05em–0.1em` to ALL CAPS text to compensate for reduced legibility.

## Line Length (Measure)

**Optimal: 45–75 characters per line.** The ideal is 66 characters (Bringhurst). Lines shorter than 45 characters cause excessive eye jumps. Lines longer than 75 characters cause readers to lose their place.

**Implementation:** Set `max-width: 65ch` on text containers. The `ch` unit is based on the width of the "0" character, making it font-aware.

## Responsive Typography with `clamp()`

Replace media-query-based font scaling with `clamp()` for fluid sizing between breakpoints.

**Formula:** `clamp(min, preferred, max)` where preferred uses viewport units.

| Element | `clamp()` Value |
|---------|----------------|
| Body | `clamp(1rem, 0.95rem + 0.25vw, 1.125rem)` |
| H3 | `clamp(1.25rem, 1rem + 1vw, 1.75rem)` |
| H2 | `clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem)` |
| H1 | `clamp(2rem, 1.5rem + 2vw, 3.5rem)` |
| Display | `clamp(2.5rem, 2rem + 3vw, 5rem)` |

## Web Font Loading

Optimize font delivery to prevent layout shift and invisible text:

1. **Use WOFF2 format** — 30% smaller than WOFF, supported by all modern browsers
2. **Set `font-display: swap`** — show fallback text immediately, swap when font loads
3. **Preload critical fonts** — `<link rel="preload" as="font" type="font/woff2" crossorigin>`
4. **Subset fonts** — strip unused glyphs for languages you do not support
5. **Limit weights** — load only the weights you use (typically 400, 500, 600, 700)

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| More than 3 font families | Visual noise, slow load times | Limit to 2-3; prefer single-family with weight variation |
| No type scale (arbitrary sizes) | Inconsistent hierarchy; sizes feel random | Adopt a modular scale ratio |
| Body text below 16px | Unreadable on mobile; fails accessibility | Minimum 16px (1rem) for body |
| Thin font weights (100-200) at small sizes | Disappears on low-DPI screens | Use 400+ for body, 300 minimum at 18px+ |
| Line length exceeding 75 characters | Readers lose their place between lines | Set `max-width: 65ch` on text containers |
| No `font-display` strategy | Flash of invisible text (FOIT) | Always set `font-display: swap` |

## Cross-Media Notes

- **Presentations:** Use 40px+ for headlines, 24px+ for body. Limit to 6-8 lines per slide. Sans-serif fonts project better on screens.
- **CVs/Resumes:** Use 10-12pt for body text, 14-16pt for section headings. Stick to widely available fonts (system fonts or Google Fonts) to avoid rendering issues.
- **Print documents:** Body at 10-12pt, line height 1.4-1.5. Serif fonts (Georgia, Garamond) are more legible in print than on screen.

## Examples

Working implementations in `examples/`:
- **`examples/type-scale-and-pairing.md`** — Complete modular type scale in CSS custom properties, Tailwind configuration, and React heading component with responsive sizing

## Review Checklist

When reviewing or building typographic systems:

- [ ] Maximum 2-3 font families used across the entire project
- [ ] Font pairing uses contrast principle (serif+sans, geometric+humanist)
- [ ] Type scale follows a mathematical ratio (Minor Third, Major Third, or Perfect Fourth)
- [ ] Body text is at minimum 16px (1rem)
- [ ] Line height is 1.4-1.6 for body text, 1.1-1.3 for headings
- [ ] Line length constrained to 45-75 characters (`max-width: 65ch` or equivalent)
- [ ] ALL CAPS text has increased letter-spacing (0.05em-0.1em)
- [ ] Responsive typography uses `clamp()` instead of breakpoint-only scaling
- [ ] Web fonts use WOFF2 format with `font-display: swap`
- [ ] Critical fonts preloaded in `<head>`
- [ ] No thin font weights (100-200) used below 18px
- [ ] Heading hierarchy is visually distinct at every level (no ambiguous sizes)
