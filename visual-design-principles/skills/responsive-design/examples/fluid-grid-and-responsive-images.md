# Fluid Grid, Responsive Images, and Touch Targets

Demonstrates a responsive card grid with CSS Grid `auto-fit`, responsive images using `srcset` and `<picture>`, and touch-target-safe interactive elements.

## Pseudocode

```
layout ResponsiveCardGrid(items):
    grid:
        columns: auto-fit, min 280px, max 1fr
        gap: 24px
    container:
        padding: clamp(16px, 4vw, 48px)
        max-width: 1200px, centered

component ResponsiveImage(src, alt, width, height):
    if above fold:
        fetchpriority: high
        loading: eager
    else:
        loading: lazy
    provide srcset at 1x, 2x, 3x
    provide AVIF and WebP sources via <picture>
    always set width and height for CLS prevention

component TouchSafeButton(label, icon):
    min-width: 44px
    min-height: 44px
    padding: extend hit area beyond visual boundary
```

## CSS

```css
/* ============================================
   Fluid responsive container
   ============================================ */
.container {
  max-width: 1200px;
  margin-inline: auto;
  padding-inline: clamp(16px, 4vw, 48px);
}

/* ============================================
   Responsive card grid — no media queries
   ============================================ */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.card {
  background: var(--color-bg-surface, #fff);
  border: 1px solid var(--color-border-default, #e2e8f0);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card__image {
  width: 100%;
  height: auto;
  display: block;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.card__body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ============================================
   Responsive typography with clamp()
   ============================================ */
h1 { font-size: clamp(2rem, 1.5rem + 2.5vw, 3.5rem); }
h2 { font-size: clamp(1.5rem, 1.25rem + 1.25vw, 2.25rem); }
body { font-size: clamp(1rem, 0.95rem + 0.25vw, 1.125rem); }

/* ============================================
   Touch-target-safe interactive elements
   ============================================ */
.touch-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 150ms ease-in-out;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
}

/* Spacing between adjacent touch targets */
.btn-group {
  display: flex;
  gap: 8px;
}

/* ============================================
   Full-height mobile layout
   ============================================ */
.full-screen {
  min-height: 100dvh;
}
```

## Tailwind CSS

```html
<!-- Fluid container -->
<div class="mx-auto max-w-screen-xl px-[clamp(16px,4vw,48px)]">

  <!-- Responsive card grid -->
  <div class="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">

    <!-- Card with responsive image -->
    <article class="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <picture>
        <source
          srcset="/img/card-1-wide.avif 800w, /img/card-1-wide-2x.avif 1600w"
          media="(min-width: 768px)"
          type="image/avif"
          sizes="(min-width: 1024px) 33vw, 50vw" />
        <source
          srcset="/img/card-1.avif 400w, /img/card-1-2x.avif 800w"
          type="image/avif"
          sizes="100vw" />
        <img
          src="/img/card-1.jpg"
          srcset="/img/card-1.jpg 400w, /img/card-1-2x.jpg 800w"
          sizes="100vw"
          alt="Feature illustration"
          width="800"
          height="450"
          loading="lazy"
          class="aspect-video w-full object-cover" />
      </picture>
      <div class="flex flex-col gap-2 p-4">
        <h3 class="text-lg font-semibold">Card Title</h3>
        <p class="text-sm text-gray-500">Description here.</p>
        <!-- Touch-safe button -->
        <button class="mt-2 inline-flex min-h-[44px] items-center justify-center
                       rounded-lg bg-blue-600 px-4 text-sm font-medium text-white
                       hover:bg-blue-700">
          Learn More
        </button>
      </div>
    </article>

    <!-- More cards... -->
  </div>

  <!-- Touch-safe icon button group -->
  <div class="flex gap-2">
    <button class="inline-flex min-h-[44px] min-w-[44px] items-center justify-center
                   rounded-lg hover:bg-gray-100"
            aria-label="Edit">
      <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><!-- icon --></svg>
    </button>
    <button class="inline-flex min-h-[44px] min-w-[44px] items-center justify-center
                   rounded-lg hover:bg-gray-100"
            aria-label="Delete">
      <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><!-- icon --></svg>
    </button>
  </div>

</div>
```

## React

```jsx
/* ---- Responsive image component ---- */
function ResponsiveImage({ src, alt, width, height, priority = false, className }) {
  return (
    <picture>
      <source
        srcSet={`${src}.avif 1x, ${src}-2x.avif 2x`}
        type="image/avif"
      />
      <source
        srcSet={`${src}.webp 1x, ${src}-2x.webp 2x`}
        type="image/webp"
      />
      <img
        src={`${src}.jpg`}
        srcSet={`${src}.jpg 1x, ${src}-2x.jpg 2x`}
        alt={alt}
        width={width}
        height={height}
        loading={priority ? 'eager' : 'lazy'}
        fetchPriority={priority ? 'high' : undefined}
        decoding="async"
        className={className}
      />
    </picture>
  );
}

/* ---- Touch-safe icon button ---- */
function IconButton({ icon: Icon, label, onClick }) {
  return (
    <button
      className="icon-btn"
      onClick={onClick}
      aria-label={label}
    >
      <Icon style={{ width: 20, height: 20 }} />
    </button>
  );
}

/* ---- Card with responsive image ---- */
function Card({ image, title, description, href }) {
  return (
    <article className="card">
      <ResponsiveImage
        src={image.src}
        alt={image.alt}
        width={800}
        height={450}
        className="card__image"
      />
      <div className="card__body">
        <h3>{title}</h3>
        <p>{description}</p>
        <a href={href} className="touch-btn" style={{ backgroundColor: 'var(--color-primary)' }}>
          Learn More
        </a>
      </div>
    </article>
  );
}

/* ---- Responsive card grid ---- */
function CardGrid({ items, priorityCount = 1 }) {
  return (
    <div className="container">
      <div className="card-grid">
        {items.map((item, i) => (
          <article key={item.id} className="card">
            <ResponsiveImage
              src={item.image.src}
              alt={item.image.alt}
              width={800}
              height={450}
              priority={i < priorityCount}
              className="card__image"
            />
            <div className="card__body">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
```

## Key Points

- **`auto-fit` + `minmax(280px, 1fr)`** creates a fully responsive card grid with zero media queries — cards reflow naturally as the viewport changes
- **`clamp(16px, 4vw, 48px)`** for container padding provides fluid spacing that scales smoothly from mobile to desktop
- **Responsive images** use `<picture>` with AVIF > WebP > JPEG fallback chain, and `srcset` for resolution switching at 1x/2x
- **`fetchpriority="high"`** is set only on the first visible image (LCP candidate); all others use `loading="lazy"`
- **Every image** has explicit `width` and `height` to prevent CLS, with `aspect-ratio` in CSS for correct sizing
- **Touch targets** enforce a 44x44px minimum via `min-width` and `min-height`, with 8px gap between adjacent buttons
- **Icon buttons** use `aria-label` since they have no visible text, and padding extends the hit area beyond the visible icon
- **`100dvh`** is used for full-screen layouts instead of `100vh` to account for mobile browser chrome
- **Typography** uses `clamp()` with a rem base — never pure `vw` — ensuring readability at all viewport sizes
