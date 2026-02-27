# Spacing System and Separation Without Borders

Demonstrates a complete 4px/8px spacing scale, Gestalt proximity in action, and separation using whitespace and background shifts instead of borders.

## Pseudocode

```
// Spacing scale — every value derived from 4px base
SPACING_SCALE = {
  1: 4px, 2: 8px, 3: 12px, 4: 16px,
  6: 24px, 8: 32px, 12: 48px, 16: 64px, 24: 96px
}

component FormSection(title, fields):
    render:
        <div style={ padding: SPACING_SCALE[6], marginBottom: SPACING_SCALE[12] }>
            <h3 style={ marginBottom: SPACING_SCALE[4] }>{title}</h3>
            for field in fields:
                // Internal gap (8px) <= 50% of external gap (24px)
                <div style={ marginBottom: SPACING_SCALE[2] }>
                    <label style={ marginBottom: SPACING_SCALE[1] }>{field.label}</label>
                    <input />
                </div>
        </div>

component SeparationDemo:
    render:
        // GOOD: whitespace separation
        <div style={ padding: SPACING_SCALE[8] }>
            <Section />
            <div style={ height: SPACING_SCALE[12] } />  // 48px gap, no border
            <Section />
        </div>

        // GOOD: background shift separation
        <div style={ background: var(--color-bg-page) }>
            <Section style={ background: var(--color-bg-surface) } />
            <Section style={ background: var(--color-bg-subtle) } />
        </div>

        // BAD: border separation
        <div>
            <Section style={ borderBottom: "1px solid gray" } />
            <Section style={ borderBottom: "1px solid gray" } />
        </div>
```

## CSS Custom Properties

```css
/* ============================================
   Spacing Scale (4px base)
   ============================================ */
:root {
  --space-1:   4px;
  --space-2:   8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;
  --space-32: 128px;
}

/* ============================================
   Gestalt Proximity: internal < 50% external
   ============================================ */
.form-group {
  padding: var(--space-6);
  margin-bottom: var(--space-12);       /* external: 48px */
}

.form-group .field {
  margin-bottom: var(--space-2);        /* internal: 8px (17% of 48px) */
}

.form-group .field label {
  margin-bottom: var(--space-1);        /* micro: 4px */
  display: block;
}

/* ============================================
   Separation without borders
   ============================================ */

/* GOOD: whitespace separation */
.section + .section {
  margin-top: var(--space-12);
}

/* GOOD: background shift separation */
.section--subtle {
  background: var(--color-bg-subtle);
  padding: var(--space-8);
}

.section--surface {
  background: var(--color-bg-surface);
  padding: var(--space-8);
}

/* BAD: border separation — avoid */
.section--bordered {
  border-bottom: 1px solid var(--color-border-default);
  padding-bottom: var(--space-6);
}
```

## Tailwind

```html
<!-- Spacing scale via Tailwind config -->
<!-- tailwind.config.js: spacing: { 1: '4px', 2: '8px', 3: '12px', ... } -->

<!-- GOOD: Gestalt proximity — internal (gap-2) << external (mb-12) -->
<div class="p-6 mb-12">
  <h3 class="mb-4 text-lg font-semibold">Billing Information</h3>
  <div class="mb-2">
    <label class="block mb-1 text-sm text-secondary">Name</label>
    <input class="w-full p-3 rounded bg-surface" />
  </div>
  <div class="mb-2">
    <label class="block mb-1 text-sm text-secondary">Email</label>
    <input class="w-full p-3 rounded bg-surface" />
  </div>
</div>

<!-- GOOD: Separation via whitespace -->
<section class="py-16">
  <div class="max-w-3xl mx-auto"><!-- content --></div>
</section>
<section class="py-16">
  <div class="max-w-3xl mx-auto"><!-- content --></div>
</section>

<!-- GOOD: Separation via background shift -->
<section class="bg-white py-16"><!-- content --></section>
<section class="bg-gray-50 py-16"><!-- content --></section>

<!-- BAD: Separation via borders -->
<section class="border-b border-gray-200 pb-8"><!-- content --></section>
<section class="border-b border-gray-200 pb-8"><!-- content --></section>
```

## React

```jsx
const SPACE = {
  1: '4px', 2: '8px', 3: '12px', 4: '16px',
  6: '24px', 8: '32px', 12: '48px', 16: '64px', 24: '96px',
};

function FormSection({ title, children }) {
  return (
    <div style={{ padding: SPACE[6], marginBottom: SPACE[12] }}>
      <h3 style={{ marginBottom: SPACE[4], fontSize: '1.125rem', fontWeight: 600 }}>
        {title}
      </h3>
      {children}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div style={{ marginBottom: SPACE[2] }}>
      <label style={{ display: 'block', marginBottom: SPACE[1], fontSize: '0.875rem' }}>
        {label}
      </label>
      {children}
    </div>
  );
}

/* Separation without borders */
function AlternatingBackground({ sections }) {
  return sections.map((section, i) => (
    <div
      key={i}
      style={{
        padding: SPACE[8],
        background: i % 2 === 0
          ? 'var(--color-bg-surface)'
          : 'var(--color-bg-subtle)',
      }}
    >
      {section}
    </div>
  ));
}
```

## Key Points

- **4px base unit**: every spacing value is a multiple of 4px -- no magic numbers
- **Gestalt proximity**: internal gaps (8px between fields) are well under 50% of external gaps (48px between sections)
- **Separation hierarchy**: whitespace first, background shifts second, borders only as last resort
- **Consistent scale**: the same tokens are used in CSS, Tailwind config, and JS -- single source of truth
- **Label-to-input gap** (4px) is smaller than **field-to-field gap** (8px), which is smaller than **section gap** (48px) -- three distinct levels of proximity
