# Three-Tier Visual Hierarchy

Demonstrates the primary/secondary/tertiary information architecture with CSS custom properties, Tailwind utilities, and React components. Includes a good/bad comparison.

## Pseudocode

```
// Three tiers — every text element maps to exactly one
TIERS = {
  primary:   { size: 2x body, weight: 700, contrast: "high" },
  secondary: { size: 1x body, weight: 400, contrast: "medium" },
  tertiary:  { size: 0.75x body, weight: 400, contrast: "low" },
}

component DashboardCard(metric):
    render:
        <div class="card">
            // Tertiary: label — small, light, muted
            <span class="text-tertiary">{metric.label}</span>
            // Primary: the star — large, bold, full contrast
            <span class="text-primary">{metric.value}</span>
            // Secondary: supporting — body size, regular weight
            <span class="text-secondary">{metric.trend}</span>
        </div>

component BadDashboardCard(metric):
    render:
        <div class="card">
            // BAD: label is bold, same size as value — no hierarchy
            <span style={ fontWeight: 700, fontSize: 16px }>{metric.label}</span>
            <span style={ fontWeight: 400, fontSize: 16px }>{metric.value}</span>
            <span style={ fontWeight: 400, fontSize: 16px }>{metric.trend}</span>
        </div>
```

## CSS Custom Properties

```css
/* ============================================
   Three-Tier Typography System
   ============================================ */
:root {
  --font-size-body: 1rem;          /* 16px baseline */

  /* Primary: the star */
  --text-primary-size:     calc(var(--font-size-body) * 2);
  --text-primary-weight:   700;
  --text-primary-color:    var(--color-text-primary);      /* >= 7:1 contrast */

  /* Secondary: supporting content */
  --text-secondary-size:   var(--font-size-body);
  --text-secondary-weight: 400;
  --text-secondary-color:  var(--color-text-secondary);    /* 4.5-7:1 contrast */

  /* Tertiary: metadata, labels, captions */
  --text-tertiary-size:    calc(var(--font-size-body) * 0.75);
  --text-tertiary-weight:  400;
  --text-tertiary-color:   var(--color-text-tertiary);     /* 3-4.5:1 contrast */
}

/* Utility classes */
.text-tier-primary {
  font-size: var(--text-primary-size);
  font-weight: var(--text-primary-weight);
  color: var(--text-primary-color);
  line-height: 1.2;
}

.text-tier-secondary {
  font-size: var(--text-secondary-size);
  font-weight: var(--text-secondary-weight);
  color: var(--text-secondary-color);
  line-height: 1.5;
}

.text-tier-tertiary {
  font-size: var(--text-tertiary-size);
  font-weight: var(--text-tertiary-weight);
  color: var(--text-tertiary-color);
  line-height: 1.5;
}

/* Label-data relationship: label always subordinate */
.label-data .label {
  font-size: var(--text-tertiary-size);
  font-weight: var(--text-tertiary-weight);
  color: var(--text-tertiary-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.label-data .data {
  font-size: var(--text-primary-size);
  font-weight: var(--text-primary-weight);
  color: var(--text-primary-color);
}
```

## Tailwind

```html
<!-- GOOD: Three-tier hierarchy — clear star, subordinate supporting text -->
<div class="p-6 bg-white rounded-lg shadow-sm">
  <!-- Tertiary: label (small, muted) -->
  <span class="text-xs font-normal text-gray-500 uppercase tracking-wide">
    Monthly Revenue
  </span>
  <!-- Primary: the star (large, bold, full contrast) -->
  <p class="text-3xl font-bold text-gray-900 mt-1">
    $48,250
  </p>
  <!-- Secondary: supporting (body, regular, medium contrast) -->
  <p class="text-base font-normal text-gray-600 mt-1">
    +12.5% from last month
  </p>
</div>

<!-- BAD: No hierarchy — everything competes -->
<div class="p-6 bg-white rounded-lg shadow-sm">
  <span class="text-base font-bold text-gray-900">Monthly Revenue</span>
  <p class="text-base font-normal text-gray-900 mt-1">$48,250</p>
  <p class="text-base font-normal text-gray-900 mt-1">+12.5% from last month</p>
</div>

<!-- GOOD: CTA hierarchy — one primary, one secondary -->
<div class="flex gap-3">
  <button class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg">
    Upgrade Plan
  </button>
  <button class="px-6 py-3 border border-gray-300 text-gray-700 font-normal rounded-lg">
    Learn More
  </button>
</div>

<!-- BAD: Two competing primaries -->
<div class="flex gap-3">
  <button class="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg">
    Upgrade Plan
  </button>
  <button class="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg">
    Contact Sales
  </button>
</div>
```

## React

```jsx
/* Tier components enforce the three-level system */

function TextPrimary({ children, as: Tag = 'span', ...props }) {
  return (
    <Tag
      style={{
        fontSize: 'var(--text-primary-size)',
        fontWeight: 'var(--text-primary-weight)',
        color: 'var(--text-primary-color)',
        lineHeight: 1.2,
      }}
      {...props}
    >
      {children}
    </Tag>
  );
}

function TextSecondary({ children, as: Tag = 'span', ...props }) {
  return (
    <Tag
      style={{
        fontSize: 'var(--text-secondary-size)',
        fontWeight: 'var(--text-secondary-weight)',
        color: 'var(--text-secondary-color)',
        lineHeight: 1.5,
      }}
      {...props}
    >
      {children}
    </Tag>
  );
}

function TextTertiary({ children, as: Tag = 'span', ...props }) {
  return (
    <Tag
      style={{
        fontSize: 'var(--text-tertiary-size)',
        fontWeight: 'var(--text-tertiary-weight)',
        color: 'var(--text-tertiary-color)',
        lineHeight: 1.5,
      }}
      {...props}
    >
      {children}
    </Tag>
  );
}

/* Dashboard card with correct label-data relationship */
function MetricCard({ label, value, trend }) {
  return (
    <div style={{ padding: 'var(--space-6)', background: 'var(--color-bg-surface)' }}>
      <TextTertiary as="span" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </TextTertiary>
      <TextPrimary as="p" style={{ marginTop: 'var(--space-1)' }}>
        {value}
      </TextPrimary>
      <TextSecondary as="p" style={{ marginTop: 'var(--space-1)' }}>
        {trend}
      </TextSecondary>
    </div>
  );
}

/* CTA hierarchy: one primary, rest secondary */
function ActionBar({ primaryLabel, primaryAction, secondaryLabel, secondaryAction }) {
  return (
    <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
      <button
        onClick={primaryAction}
        style={{
          padding: 'var(--space-3) var(--space-6)',
          background: 'var(--color-action-primary)',
          color: 'white',
          fontWeight: 600,
          borderRadius: 'var(--radius-default)',
          border: 'none',
        }}
      >
        {primaryLabel}
      </button>
      <button
        onClick={secondaryAction}
        style={{
          padding: 'var(--space-3) var(--space-6)',
          background: 'transparent',
          color: 'var(--color-text-secondary)',
          fontWeight: 400,
          borderRadius: 'var(--radius-default)',
          border: '1px solid var(--color-border-default)',
        }}
      >
        {secondaryLabel}
      </button>
    </div>
  );
}
```

## Key Points

- **Three tiers only**: primary (2x, bold, high contrast), secondary (1x, regular, medium), tertiary (0.75x, regular, low)
- **One star per card/section**: the metric value is the star, not the label
- **Labels subordinate to data**: labels are tertiary (small, muted, uppercase), data is primary (large, bold, full contrast)
- **CTA hierarchy**: one filled primary button, supporting actions use outlined/ghost styles
- **Emphasize by de-emphasizing**: the bad example shows that when everything is the same size/weight/color, nothing stands out
- **Lever independence**: size and weight are adjusted separately -- the primary uses size (2x) and weight (700), but tertiary uses only size (0.75x) with regular weight
