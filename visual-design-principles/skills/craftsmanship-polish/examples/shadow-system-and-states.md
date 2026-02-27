# Shadow Elevation System, Skeleton Screen, and Empty State

Demonstrates a complete 5-level layered shadow system, a skeleton screen with shimmer animation, and an empty state component with CTA.

## Pseudocode

```
tokens ElevationSystem:
    shadow-0: none
    shadow-1: layered(offset-y 1px blur 2px alpha 0.06, offset-y 1px blur 3px alpha 0.1)
    shadow-2: layered(offset-y 4px blur 6px alpha 0.07, offset-y 2px blur 4px alpha 0.06)
    shadow-3: layered(offset-y 10px blur 15px alpha 0.1, offset-y 4px blur 6px alpha 0.05)
    shadow-4: layered(offset-y 20px blur 25px alpha 0.1, offset-y 8px blur 10px alpha 0.04)

component Card(elevation = 1):
    apply shadow from ElevationSystem[elevation]
    on hover: transition to ElevationSystem[elevation + 1] over 200ms

component SkeletonCard:
    render placeholder shapes matching CardContent layout
    apply shimmer animation: left-to-right gradient, 1.5s cycle

component EmptyState(icon, heading, description, ctaLabel, onCta):
    render centered layout:
        icon (48px, muted color)
        heading (semibold)
        description (secondary text, max-width 360px)
        primary button with ctaLabel, onClick = onCta
```

## CSS

```css
/* ============================================
   5-Level Shadow Elevation System
   ============================================ */
:root {
  --shadow-0: none;
  --shadow-1: 0 1px 2px rgba(0, 0, 0, 0.06),
              0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-2: 0 4px 6px rgba(0, 0, 0, 0.07),
              0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-3: 0 10px 15px rgba(0, 0, 0, 0.1),
              0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-4: 0 20px 25px rgba(0, 0, 0, 0.1),
              0 8px 10px rgba(0, 0, 0, 0.04);

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}

.card {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-1);
  transition: box-shadow 200ms ease-in-out;
}

.card:hover {
  box-shadow: var(--shadow-2);
}

.dropdown { box-shadow: var(--shadow-2); }
.modal    { box-shadow: var(--shadow-3); }
.popover  { box-shadow: var(--shadow-4); }

/* ============================================
   Skeleton Screen with Shimmer
   ============================================ */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-subtle, #f1f5f9) 25%,
    var(--color-bg-muted, #e2e8f0) 50%,
    var(--color-bg-subtle, #f1f5f9) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-avatar  { width: 48px; height: 48px; border-radius: var(--radius-full); }
.skeleton-title   { width: 60%; height: 20px; border-radius: var(--radius-sm); }
.skeleton-text    { width: 100%; height: 14px; border-radius: var(--radius-sm); margin-top: 8px; }
.skeleton-text-sm { width: 75%; height: 14px; border-radius: var(--radius-sm); margin-top: 8px; }

/* ============================================
   Empty State
   ============================================ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 64px 24px;
  gap: 16px;
}

.empty-state__icon {
  width: 48px;
  height: 48px;
  color: var(--color-text-tertiary, #94a3b8);
}

.empty-state__heading {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.empty-state__description {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  max-width: 360px;
  margin: 0;
}
```

## Tailwind CSS

```html
<!-- Card with layered shadow and hover elevation -->
<article class="rounded-lg border border-gray-200 bg-white p-6
               shadow-[0_1px_2px_rgba(0,0,0,0.06),0_1px_3px_rgba(0,0,0,0.1)]
               transition-shadow duration-200 ease-in-out
               hover:shadow-[0_4px_6px_rgba(0,0,0,0.07),0_2px_4px_rgba(0,0,0,0.06)]">
  <h3 class="text-lg font-semibold">Card Title</h3>
  <p class="mt-2 text-sm text-gray-500">Card content goes here.</p>
</article>

<!-- Skeleton screen -->
<div class="flex flex-col gap-2 rounded-lg border border-gray-200 p-6">
  <div class="h-12 w-12 animate-pulse rounded-full bg-gray-200"></div>
  <div class="h-5 w-3/5 animate-pulse rounded bg-gray-200"></div>
  <div class="h-3.5 w-full animate-pulse rounded bg-gray-200"></div>
  <div class="h-3.5 w-3/4 animate-pulse rounded bg-gray-200"></div>
</div>

<!-- Empty state -->
<div class="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center">
  <svg class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
  </svg>
  <h3 class="text-lg font-semibold">No items yet</h3>
  <p class="max-w-sm text-sm text-gray-500">Get started by creating your first item.</p>
  <button class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white
                 transition-transform duration-150 ease-in-out
                 hover:bg-blue-700 active:scale-[0.98]">
    Create Item
  </button>
</div>
```

## React

```jsx
/* ---- Elevation tokens (use in a theme or CSS module) ---- */
const shadows = {
  0: 'none',
  1: '0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.1)',
  2: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
  3: '0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)',
  4: '0 20px 25px rgba(0,0,0,0.1), 0 8px 10px rgba(0,0,0,0.04)',
};

/* ---- Card with elevation ---- */
function Card({ elevation = 1, children }) {
  return (
    <article className="card" style={{ boxShadow: shadows[elevation] }}>
      {children}
    </article>
  );
}

/* ---- Skeleton Card ---- */
function SkeletonCard() {
  return (
    <div className="card">
      <div className="skeleton skeleton-avatar" />
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text-sm" />
    </div>
  );
}

/* ---- Empty State ---- */
function EmptyState({ icon: Icon, heading, description, ctaLabel, onCta }) {
  return (
    <div className="empty-state">
      <Icon className="empty-state__icon" />
      <h3 className="empty-state__heading">{heading}</h3>
      <p className="empty-state__description">{description}</p>
      <button className="btn btn--primary" onClick={onCta}>
        {ctaLabel}
      </button>
    </div>
  );
}

/* ---- Usage ---- */
function ProjectList({ projects, isLoading }) {
  if (isLoading) {
    return (
      <div className="card-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <EmptyState
        icon={InboxIcon}
        heading="No projects yet"
        description="Create your first project to get started."
        ctaLabel="New Project"
        onCta={() => navigate('/projects/new')}
      />
    );
  }

  return (
    <div className="card-grid">
      {projects.map((p) => (
        <Card key={p.id} elevation={1}>
          <h3>{p.name}</h3>
          <p>{p.description}</p>
        </Card>
      ))}
    </div>
  );
}
```

## Key Points

- **Layered shadows** use two `box-shadow` values per level — a tight shadow for contact and a diffuse shadow for ambient light — producing far more realistic depth than a single value
- **Elevation increases** on hover with a `200ms ease-in-out` transition, giving cards a subtle lift effect
- **Skeleton elements match content shape** — avatar, title, and text lines mirror the actual card layout
- **Shimmer runs at 1.5s** with a left-to-right gradient (perceived as faster than opacity pulsing)
- **Empty state** includes all four required elements: icon, heading, description, and CTA
- **Border-radius tokens** are applied consistently: `--radius-md` for cards, `--radius-sm` for skeleton shapes, `--radius-full` for avatars
- **Active state** uses `scale(0.98)` for tactile button feedback at 150ms duration
