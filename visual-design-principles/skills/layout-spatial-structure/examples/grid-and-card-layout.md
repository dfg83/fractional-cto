# Grid System and Responsive Card Layout

Demonstrates a 12-column grid foundation and a responsive card grid using CSS Grid `auto-fit` with `minmax()`.

## Pseudocode

```
layout PageLayout(sidebar, main):
    container:
        max-width: 1200px, centered
        grid: 12 columns, 24px gutter
    sidebar:
        span: 3 columns
    main:
        span: 9 columns
    on mobile (< 768px):
        sidebar: hidden or collapsed
        main: span 12 columns

layout CardGrid(cards):
    grid:
        columns: auto-fit, min 280px, max 1fr
        gap: 24px
    each card:
        padding: 24px
        border-radius: 8px
        internal spacing: 8px between elements
```

## CSS — 12-Column Grid Foundation

```css
/* ============================================
   12-Column Grid System
   ============================================ */
:root {
  --grid-columns: 12;
  --grid-gutter: 24px;
  --grid-margin: 24px;
  --container-max: 1200px;

  /* 8-point spacing scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;
}

.container {
  max-width: var(--container-max);
  margin-inline: auto;
  padding-inline: var(--grid-margin);
}

/* Page layout: mobile-first, single column by default */
.page-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--grid-gutter);
}

@media (min-width: 768px) {
  .page-layout {
    grid-template-columns: 3fr 9fr;
  }
}

/* ============================================
   Responsive Card Grid
   auto-fit reflows cards without media queries
   ============================================ */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
}

.card {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: 8px;
  padding: var(--space-4);

  /* Internal spacing: tighter than grid gap (Gestalt proximity) */
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.card__title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.card__description {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}
```

## Tailwind CSS

```html
<!-- Page layout: sidebar + main -->
<div class="mx-auto max-w-screen-xl px-6">
  <div class="grid grid-cols-1 gap-6 md:grid-cols-12">
    <aside class="hidden md:col-span-3 md:block">
      <!-- Sidebar content -->
    </aside>
    <main class="md:col-span-9">
      <!-- Main content -->
    </main>
  </div>
</div>

<!-- Responsive card grid -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  <article class="flex flex-col gap-2 rounded-lg border border-gray-200 p-6">
    <h3 class="text-lg font-semibold">Card Title</h3>
    <p class="text-sm text-gray-500">Card description goes here.</p>
  </article>
  <!-- More cards... -->
</div>
```

## React

```jsx
function PageLayout({ sidebar, children }) {
  return (
    <div className="container">
      <div className="page-layout">
        <aside className="sidebar">{sidebar}</aside>
        <main className="main">{children}</main>
      </div>
    </div>
  );
}

function CardGrid({ items }) {
  return (
    <div className="card-grid">
      {items.map((item) => (
        <article key={item.id} className="card">
          <h3 className="card__title">{item.title}</h3>
          <p className="card__description">{item.description}</p>
        </article>
      ))}
    </div>
  );
}
```

## Key Points

- **12-column grid** uses `grid-template-columns: 3fr 9fr` for sidebar layouts — columns are proportional, not fixed
- **Card grid** uses `repeat(auto-fit, minmax(280px, 1fr))` — cards reflow without any media queries
- **Internal card spacing** (8px via `gap: var(--space-2)`) is smaller than **grid gap** (24px via `gap: var(--space-4)`), enforcing Gestalt proximity
- All spacing values are on the **8-point scale** (4, 8, 16, 24, 32, 48, 64)
- Container is **max-width constrained** and **centered** with `margin-inline: auto`
- Mobile layout collapses to single column via one media query on the page grid
