# Design Evaluation Workflow -- Fictional Landing Page

Demonstrates the complete 8-dimension evaluation workflow applied to a fictional SaaS landing page for "Acme Analytics."

## Step 1: 50ms First Impression

```
First Impression Assessment
===========================
Design: Acme Analytics landing page
Impression: "Clean but flat — good structure, lacks personality"
Confidence: Moderate
Initial estimate: 26-30 / 40
```

The 50ms glance reveals a well-structured layout with clear sections, but the page feels generic and template-like. No immediate red flags, but nothing memorable either.

## Step 2: Anti-Pattern Rapid Screening

```
Anti-Pattern Checklist (<60 seconds)
=====================================
[ ] 1. More than 3 font families?               NO  — 2 families (Inter + monospace)
[X] 2. Text below 4.5:1 contrast?               YES — Gray subtitle is #a1a1aa on #fff (3.6:1)
[ ] 3. Elements visibly misaligned?              NO  — Grid is consistent
[X] 4. Inconsistent spacing?                     YES — Hero has 96px bottom gap, Features has 48px
[ ] 5. No clear focal point?                     NO  — Hero CTA is prominent
[ ] 6. Color-only status indicators?             NO  — Not applicable on landing page
[ ] 7. Low-resolution or stretched images?       NO  — SVG illustrations used
[X] 8. Inconsistent border-radius or shadows?    YES — Cards use 8px, buttons use 4px
[ ] 9. Content touching container edges?         NO  — Proper padding throughout
[X] 10. No visual personality?                   YES — Could be any SaaS product

Red flags: 4 / 10
Priority issues: contrast failure, spacing inconsistency, style inconsistency, weak expression
```

## Step 3: Dimension-by-Dimension Audit

### Scorecard

```
8-Dimension Scorecard: Acme Analytics Landing Page
===================================================

| #  | Dimension     | Score | Notes                                           |
|----|---------------|-------|-------------------------------------------------|
| 1  | Layout        | 4     | 12-col grid, good alignment, responsive.        |
|    |               |       | Card grid uses auto-fit correctly.               |
| 2  | Typography    | 4     | Inter at 16px body, 1.25 scale, good pairing.   |
|    |               |       | Line length controlled. One heading too light.   |
| 3  | Color         | 3     | Blue primary, gray neutral. No secondary hue.    |
|    |               |       | Subtitle fails AA contrast. No shade scale.      |
| 4  | Whitespace    | 3     | Good macro whitespace in hero. Inconsistent      |
|    |               |       | section gaps (96px vs 48px). Internal spacing OK. |
| 5  | Hierarchy     | 4     | Clear hero CTA. 3 tiers visible. Feature cards   |
|    |               |       | compete slightly — all same visual weight.        |
| 6  | Consistency   | 3     | Most components match. Border-radius conflict     |
|    |               |       | (8px cards, 4px buttons). No design tokens file.  |
| 7  | Craftsmanship | 4     | SVG icons crisp. Shadows subtle. CLS < 0.05.     |
|    |               |       | Loading states present. One image has no alt.     |
| 8  | Expression    | 2     | Generic SaaS template feel. No illustrations,     |
|    |               |       | no brand motifs, no motion. Interchangeable.      |
|====|===============|=======|=================================================|
|    | TOTAL         | 27/40 | Rating: ADEQUATE                                |
```

### Detailed Notes Per Dimension

**Layout (4/5):** The page uses a proper 12-column grid. The hero section spans full width with centered content. Feature cards use `repeat(auto-fit, minmax(300px, 1fr))` and reflow correctly on mobile. Sidebar navigation collapses to hamburger. One minor issue: the testimonial section uses a different max-width than the rest of the page (1000px vs 1200px), creating a subtle misalignment.

**Typography (4/5):** Inter is a solid choice. Body is 16px with 1.5 line height. Headings follow a 1.25 scale (16, 20, 25, 31, 39). Line length is constrained to ~65ch. One heading in the pricing section uses `font-weight: 300`, which is too light for the heading hierarchy and creates a weak focal point.

**Color (3/5):** Blue-600 primary works. Gray-50/100/200 neutrals are appropriate. However: the subtitle gray (#a1a1aa) fails AA contrast at 3.6:1 on white — needs to be at minimum #767676. There is no secondary accent color, making the palette monotone. No shade scale is defined — colors are ad-hoc hex values, not design tokens.

**Whitespace (3/5):** The hero section has generous whitespace (~55% ratio — appropriate for a marketing page). However, section gaps are inconsistent: 96px after the hero, 48px between Features and Testimonials, 64px before the footer. Standard deviation is ~20px, well above the 8px target. Internal card spacing is consistent (16px padding, 8px gaps).

**Hierarchy (4/5):** The hero has a clear focal point: large heading + blue CTA button. The 3-tier structure works (hero > feature cards > footer links). However, all three feature cards have identical visual weight — one key differentiator or a "most popular" treatment would strengthen the hierarchy. The pricing section CTA is the same size and color as the hero CTA, diluting the primary action.

**Consistency (3/5):** Most components are internally consistent. However: cards use `border-radius: 8px` while buttons use `border-radius: 4px` — these should either match or follow a documented radius scale. Input fields use yet another radius (6px). No `design-tokens.css` or Tailwind config defines these values — they are hardcoded throughout.

**Craftsmanship (4/5):** SVG illustrations are crisp on retina. Shadows are subtle (`0 1px 3px rgba(0,0,0,0.1)`). CLS measured at 0.04 — well under 0.1. Loading states exist for the pricing toggle. One image in the testimonial section has no alt text. Button hover transitions use `transition: all 150ms` — should be scoped to specific properties.

**Expression (2/5):** The page looks like a template. There are no custom illustrations, no brand-specific visual motifs, no micro-interactions beyond basic hover effects, and no motion. The design is competent but could belong to any SaaS product. A competitor could not distinguish this from their own marketing page.

## Step 4: Score and Prioritize

```
Prioritized Improvement Plan
==============================

Priority 1 — Structural Fixes (Low Effort, High Impact)
--------------------------------------------------------
1. Fix subtitle contrast: change #a1a1aa to #737373 (passes 4.5:1)
2. Normalize section gaps: use 64px consistently (±8px max)
3. Define border-radius scale: 4px (small), 8px (medium), 12px (large)
4. Create design tokens file for colors, spacing, and radii

Priority 2 — Hierarchy Refinement (Medium Effort)
--------------------------------------------------
5. Differentiate feature cards (highlight one as primary)
6. Reduce secondary CTA prominence vs hero CTA
7. Fix pricing heading weight (300 → 600)

Priority 3 — Expression Enhancement (Higher Effort)
----------------------------------------------------
8. Add custom illustrations or brand-specific iconography
9. Introduce a secondary accent color for visual variety
10. Add micro-interactions (button press, card hover lift, scroll reveals)
11. Define a shade scale for the primary blue (50-950)

Expected score after Priority 1: 31/40 (Good)
Expected score after all priorities: 35-37/40 (Good-Excellent)
```

## Scorecard Template

Use this template for your own evaluations:

```markdown
## 8-Dimension Scorecard: [Design Name]

| #  | Dimension     | Score | Notes |
|----|---------------|-------|-------|
| 1  | Layout        |   /5  |       |
| 2  | Typography    |   /5  |       |
| 3  | Color         |   /5  |       |
| 4  | Whitespace    |   /5  |       |
| 5  | Hierarchy     |   /5  |       |
| 6  | Consistency   |   /5  |       |
| 7  | Craftsmanship |   /5  |       |
| 8  | Expression    |   /5  |       |
|====|===============|=======|=======|
|    | TOTAL         |  /40  | Rating: [Poor/Below Average/Adequate/Good/Excellent] |
```

## Key Points

- **50ms first impression** correlates strongly with extended evaluation -- trust your initial gut reaction as a directional signal
- **Anti-pattern screening** catches surface-level issues in under 60 seconds before investing in detailed scoring
- **Structural dimensions (1-5) are scored first** because they explain the most variance in perceived quality
- **Each dimension maps to a specific principle skill** -- invoke the relevant skill for detailed criteria when scoring
- **The prioritized improvement plan orders fixes by effort-to-impact ratio** -- structural fixes first, expression last
- **Measurable proxies** (contrast ratios, whitespace percentage, CLS, grid adherence) ground subjective scoring in data
- **The scorecard template** provides a repeatable format for comparing designs across projects or iterations
