---
name: responsive-design
description: This skill should be used when the user is implementing responsive layouts, choosing breakpoints, building mobile-first designs, using CSS container queries, implementing responsive images (srcset, picture), sizing touch targets, designing responsive navigation, or adapting tables for mobile. Covers mobile-first philosophy, breakpoint strategy, fluid grids with CSS Grid, container queries, responsive images, touch target sizing (44x44px minimum), and responsive tables.
version: 1.0.0
---

# Mobile-First Is Not a Technical Strategy — It Is a Content Strategy

Mobile-first forces content prioritization. When you design for 320px first, you must decide what actually matters. Desktop is the easy case — there is room for everything. Mobile reveals what is essential. Start narrow, enhance wide. Use `min-width` media queries exclusively (progressive enhancement).

## Breakpoint Reference

Define breakpoints based on common device classes. Use `min-width` (mobile-first) exclusively.

| Name | Range | Min-Width Query | Typical Devices |
|------|-------|----------------|-----------------|
| **xs** | 0-479px | (base styles) | Small phones |
| **sm** | 480-639px | `@media (min-width: 480px)` | Large phones |
| **md** | 640-767px | `@media (min-width: 640px)` | Small tablets |
| **lg** | 768-1023px | `@media (min-width: 768px)` | Tablets, small laptops |
| **xl** | 1024-1279px | `@media (min-width: 1024px)` | Laptops, desktops |
| **2xl** | 1280px+ | `@media (min-width: 1280px)` | Large desktops |

**Rule:** Design for xs first. Add complexity at each breakpoint. Never start with desktop and subtract.

## Fluid Grids

Use CSS Grid `auto-fit`/`auto-fill` with `minmax()` for grids that reflow without media queries. Use `clamp()` for fluid sizing that interpolates between a minimum and maximum.

```css
/* Responsive card grid — no media queries needed */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

/* Fluid container padding */
.container {
  padding-inline: clamp(16px, 4vw, 48px);
  max-width: 1200px;
  margin-inline: auto;
}
```

## Container Queries

Container queries decouple component responsiveness from the viewport. A card in a sidebar and a card in the main content area can respond to their own available space.

```css
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card { flex-direction: row; }
}

@container card (max-width: 399px) {
  .card { flex-direction: column; }
}
```

**Use container queries when:** a component appears in multiple layout contexts (sidebar, main, modal) and must adapt to its container, not the viewport.

## Responsive Images

Use `srcset` for resolution switching and `<picture>` for art direction. Lazy-load below-fold images. Set `fetchpriority="high"` on the LCP image.

| Attribute | Purpose |
|-----------|---------|
| `srcset` + `sizes` | Browser selects the best resolution based on viewport and pixel density |
| `<picture>` + `<source>` | Art direction — different crops or aspect ratios per breakpoint |
| `loading="lazy"` | Defer loading for images below the fold |
| `fetchpriority="high"` | Prioritize the Largest Contentful Paint image |
| `width` + `height` | Reserve space to prevent CLS (see `craftsmanship-polish` for CLS rules) |

```html
<picture>
  <source srcset="/img/hero-wide.avif" media="(min-width: 768px)" type="image/avif" />
  <source srcset="/img/hero-wide.webp" media="(min-width: 768px)" type="image/webp" />
  <source srcset="/img/hero-narrow.avif" type="image/avif" />
  <source srcset="/img/hero-narrow.webp" type="image/webp" />
  <img src="/img/hero-narrow.jpg" alt="Hero" width="800" height="600"
       fetchpriority="high" decoding="async" />
</picture>
```

## Responsive Typography

Use `clamp()` for fluid type scaling. See the `typography` skill for the full `clamp()` value table. Never use pure `vw` alone — it becomes unreadable on small screens and enormous on large ones.

## Touch Targets

Apply the 44x44px minimum touch target and 8px spacing rules from the `accessibility-inclusive-design` skill. On mobile, extend hit areas with padding:

```css
/* Extend hit area with padding */
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
}
```

## Navigation Patterns

Choose the navigation pattern based on item count and importance.

| Pattern | Items | Best For | Mobile Behavior |
|---------|-------|----------|-----------------|
| **Hamburger menu** | 5+ | Content-heavy sites, secondary nav | Slide-in drawer or full-screen overlay |
| **Bottom tabs** | 3-5 | Mobile apps, high-frequency nav | Fixed at bottom, always visible |
| **Priority+** | Variable | Primary nav with overflow | Show as many items as fit, collapse rest into "More" |
| **Full-screen overlay** | Any | Marketing sites, minimal nav | Covers entire viewport with large tap targets |

**Rule:** On mobile, the most important actions must be reachable with one thumb. Place primary navigation within the bottom 60% of the screen when possible.

## Responsive Tables

Tables on mobile require adaptation. Choose the pattern based on data complexity.

| Pattern | When to Use | How |
|---------|-------------|-----|
| **Horizontal scroll** | Simple data, few columns | `overflow-x: auto` on table wrapper |
| **Card transformation** | Complex data, many columns | Each row becomes a stacked card on mobile |
| **Column priority** | Some columns more important | Hide low-priority columns on small screens, show on hover or expand |

## Mobile Viewport Height

Use `100dvh` (dynamic viewport height) instead of `100vh` on mobile. The `vh` unit does not account for browser chrome (address bar, toolbar), causing content to be hidden behind UI elements.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Fixed-width layouts (e.g., `width: 960px`) | Broken on every viewport except one | Use fluid widths, `max-width`, and `minmax()` |
| Horizontal scroll on body | Frustrating, signals broken layout | Audit for elements exceeding viewport width |
| Tiny touch targets (<44px) | Misclicks, accessibility failure | Apply touch target rules (see `accessibility-inclusive-design` skill) |
| Desktop-first with `max-width` overrides | Fragile, constantly undoing styles | Rewrite mobile-first with `min-width` queries |
| Media query soup (20+ breakpoints) | Unmaintainable, overlapping rules | Consolidate to 4-6 breakpoints, use fluid techniques |
| `100vh` on mobile | Content hidden behind browser chrome | Use `100dvh` or `100svh` |
| Pure `vw` for font size | Unreadable on mobile, enormous on 4K | Use `clamp()` (see `typography` skill) |

## Cross-Media Notes

- **Responsive is web-specific** but the principle of "adapt to the medium" is universal. Presentations must work on projector screens and laptop monitors. Documents must work in A4 and Letter formats.
- **Presentations:** Design slides at 16:9 but test at lower resolutions. Ensure text is readable from the back of the room (minimum 24pt body, 36pt headings).
- **Documents:** Use responsive margins — wider for print, narrower for screen reading. Test PDF rendering on mobile devices.

## Examples

Working implementations in `examples/`:
- **`examples/fluid-grid-and-responsive-images.md`** — Responsive card grid with auto-fit, responsive images with srcset, and touch-target-safe buttons in CSS/Tailwind/React

## Review Checklist

When reviewing or building responsive designs:

- [ ] Styles are written mobile-first using `min-width` media queries (no `max-width`)
- [ ] Breakpoints align with the 6-level reference table (xs through 2xl)
- [ ] Card grids use `auto-fit`/`auto-fill` with `minmax()` for media-query-free reflow
- [ ] Container queries used for components that appear in multiple layout contexts
- [ ] All images use `srcset` + `sizes` or `<picture>` for responsive loading
- [ ] LCP image has `fetchpriority="high"` and all below-fold images have `loading="lazy"`
- [ ] All images have `width` and `height` attributes (see `craftsmanship-polish` for CLS rules)
- [ ] Touch targets meet accessibility requirements (see `accessibility-inclusive-design` skill)
- [ ] Typography uses `clamp()` for fluid scaling (see `typography` skill for values)
- [ ] `100dvh` used instead of `100vh` for full-height mobile layouts
- [ ] Tables adapt on mobile (horizontal scroll, card transformation, or column priority)
- [ ] Navigation pattern is appropriate for item count and collapses gracefully on mobile
