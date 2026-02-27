# Purposeful Motion and Layout Variety

Demonstrates CSS transitions with `prefers-reduced-motion` handling, staggered list reveals, and a landing page section layout pattern with alternating density.

## Pseudocode

```
animation FadeInUp(element, delay = 0):
    initial: opacity 0, translateY 16px
    animate to: opacity 1, translateY 0
    duration: 300ms, ease-out
    delay: delay
    if prefers-reduced-motion: skip animation, show immediately

layout LandingPage:
    section Hero: full-width, large heading, CTA, hero image
    section Features: 3-column card grid (dense)
    section FullWidthBreak: edge-to-edge image or color block (open)
    section TextMedia: 50/50 split text + image, alternating sides
    section SocialProof: logo row or stat counters (open)
    section CTA: centered heading + button
```

## CSS

```css
/* ============================================
   Fade-in-up entrance animation
   ============================================ */
.fade-in-up {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 300ms ease-out, transform 300ms ease-out;
}

.fade-in-up.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* Stagger children: each child delays 75ms more than the previous */
.stagger > .fade-in-up:nth-child(1) { transition-delay: 0ms; }
.stagger > .fade-in-up:nth-child(2) { transition-delay: 75ms; }
.stagger > .fade-in-up:nth-child(3) { transition-delay: 150ms; }
.stagger > .fade-in-up:nth-child(4) { transition-delay: 225ms; }

/* ============================================
   Reduced motion: disable non-essential animation
   ============================================ */
@media (prefers-reduced-motion: reduce) {
  .fade-in-up {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

/* ============================================
   Interactive element transitions
   ============================================ */
.btn {
  transition: background-color 150ms ease-in-out, transform 150ms ease-in-out;
}

.btn:hover {
  background-color: var(--color-primary-hover);
}

.btn:active {
  transform: scale(0.98);
}

/* ============================================
   Layout variety: alternating section density
   ============================================ */
.section-hero {
  padding: 96px 24px;
  text-align: center;
}

.section-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  padding: 64px 24px;
}

.section-full-width {
  width: 100%;
  padding: 0;
  background: var(--color-bg-accent, #f8fafc);
}

.section-full-width img {
  width: 100%;
  height: auto;
  display: block;
}

.section-text-media {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
  padding: 64px 24px;
}

.section-text-media.reversed {
  direction: rtl;
}

.section-text-media.reversed > * {
  direction: ltr;
}

.section-social-proof {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48px;
  padding: 48px 24px;
}

@media (max-width: 767px) {
  .section-text-media {
    grid-template-columns: 1fr;
  }

  .section-text-media.reversed {
    direction: ltr;
  }
}
```

## Tailwind CSS

```html
<!-- Fade-in-up with stagger (use Intersection Observer to add 'is-visible') -->
<div class="stagger grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  <article class="fade-in-up rounded-lg border p-6 opacity-0 translate-y-4
                  transition-all duration-300 ease-out
                  [&.is-visible]:opacity-100 [&.is-visible]:translate-y-0">
    <h3 class="text-lg font-semibold">Feature One</h3>
    <p class="mt-2 text-sm text-gray-500">Description here.</p>
  </article>
  <!-- Repeat for more cards with stagger delay via style="transition-delay: 75ms" -->
</div>

<!-- Reduced motion handled via Tailwind -->
<button class="rounded-lg bg-blue-600 px-4 py-2 text-white
               transition-all duration-150 ease-in-out
               hover:bg-blue-700 active:scale-[0.98]
               motion-reduce:transition-none">
  Get Started
</button>

<!-- Layout variety: alternating sections -->
<!-- Hero (open) -->
<section class="px-6 py-24 text-center">
  <h1 class="text-4xl font-bold">Build Something Great</h1>
  <p class="mx-auto mt-4 max-w-xl text-lg text-gray-600">Subtitle goes here.</p>
  <button class="mt-8 rounded-lg bg-blue-600 px-6 py-3 text-white">Start Free</button>
</section>

<!-- Card grid (dense) -->
<section class="grid grid-cols-1 gap-6 px-6 py-16 sm:grid-cols-2 lg:grid-cols-3">
  <!-- Feature cards -->
</section>

<!-- Full-width break (open) -->
<section class="bg-gray-50">
  <img src="/images/hero-wide.avif" alt="" class="block w-full" width="1440" height="480" />
</section>

<!-- Text + Media (dense) -->
<section class="grid grid-cols-1 items-center gap-12 px-6 py-16 md:grid-cols-2">
  <div>
    <h2 class="text-2xl font-bold">Feature Highlight</h2>
    <p class="mt-4 text-gray-600">Explanation of the benefit.</p>
  </div>
  <img src="/images/feature.avif" alt="" class="rounded-lg" width="600" height="400" />
</section>

<!-- Social proof (open) -->
<section class="flex flex-wrap items-center justify-center gap-12 px-6 py-12">
  <img src="/logos/company-a.svg" alt="Company A" class="h-8 opacity-60" />
  <img src="/logos/company-b.svg" alt="Company B" class="h-8 opacity-60" />
  <img src="/logos/company-c.svg" alt="Company C" class="h-8 opacity-60" />
</section>
```

## React

```jsx
import { useEffect, useRef, useState } from 'react';

/* ---- Intersection Observer hook for reveal-on-scroll ---- */
function useReveal(options = { threshold: 0.15 }) {
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.unobserve(el);
      }
    }, options);

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return [ref, isVisible];
}

/* ---- Animated card with stagger ---- */
function AnimatedCard({ title, description, delay = 0 }) {
  const [ref, isVisible] = useReveal();

  return (
    <article
      ref={ref}
      className="card fade-in-up"
      style={{
        transitionDelay: `${delay}ms`,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(16px)',
      }}
    >
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  );
}

/* ---- Feature grid with staggered reveal ---- */
function FeatureGrid({ features }) {
  return (
    <section className="section-cards">
      {features.map((f, i) => (
        <AnimatedCard
          key={f.id}
          title={f.title}
          description={f.description}
          delay={i * 75}
        />
      ))}
    </section>
  );
}

/* ---- Text + Media section (alternating) ---- */
function TextMediaSection({ heading, body, imageSrc, reversed = false }) {
  return (
    <section className={`section-text-media ${reversed ? 'reversed' : ''}`}>
      <div>
        <h2>{heading}</h2>
        <p>{body}</p>
      </div>
      <img src={imageSrc} alt="" width={600} height={400} loading="lazy" />
    </section>
  );
}

/* ---- Landing page with layout variety ---- */
function LandingPage({ features }) {
  return (
    <main>
      {/* Hero (open) */}
      <section className="section-hero">
        <h1>Build Something Great</h1>
        <p>Subtitle goes here.</p>
        <button className="btn">Start Free</button>
      </section>

      {/* Card grid (dense) */}
      <FeatureGrid features={features} />

      {/* Full-width break (open) */}
      <section className="section-full-width">
        <img src="/images/hero-wide.avif" alt="" width={1440} height={480} />
      </section>

      {/* Text + Media (dense) */}
      <TextMediaSection
        heading="Feature One"
        body="Explanation of the benefit."
        imageSrc="/images/feature-1.avif"
      />

      {/* Text + Media reversed (dense) */}
      <TextMediaSection
        heading="Feature Two"
        body="Another benefit explained."
        imageSrc="/images/feature-2.avif"
        reversed
      />

      {/* Social proof (open) */}
      <section className="section-social-proof">
        <img src="/logos/a.svg" alt="Company A" />
        <img src="/logos/b.svg" alt="Company B" />
        <img src="/logos/c.svg" alt="Company C" />
      </section>
    </main>
  );
}
```

## Key Points

- **Fade-in-up** animates only `opacity` and `transform` — both GPU-composited, avoiding layout thrashing
- **Stagger delay** of 75ms between cards creates a sequential reveal that draws the eye without feeling slow
- **`prefers-reduced-motion: reduce`** removes all transition and transform effects, showing content immediately
- **Layout variety** alternates between dense sections (card grid, text+media) and open sections (hero, full-width image, social proof) for visual rhythm
- **Section-text-media** uses CSS Grid `1fr 1fr` and `direction: rtl` to reverse content order without changing DOM structure
- **Intersection Observer** triggers animation only when elements enter the viewport — no wasted motion off-screen
- **All images** include `width` and `height` attributes to prevent CLS, and below-fold images use `loading="lazy"`
