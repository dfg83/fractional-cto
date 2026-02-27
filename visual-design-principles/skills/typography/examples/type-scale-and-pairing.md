# Type Scale and Font Pairing

Demonstrates a complete modular type scale using CSS custom properties, Tailwind configuration, and a React heading component with responsive sizing.

## Pseudocode

```
config TypeScale:
    base: 16px
    ratio: 1.25 (Major Third)
    steps:
        sm:      base / ratio      = 12.8px
        body:    base               = 16px
        lg:      base * ratio       = 20px
        xl:      base * ratio^2     = 25px
        2xl:     base * ratio^3     = 31.25px
        3xl:     base * ratio^4     = 39.06px
        display: base * ratio^5     = 48.83px

    line-heights:
        body:     1.5
        headings: 1.2
        display:  1.1

component Heading(level, children):
    tag = "h" + level
    size = scale step based on level
    render:
        <tag style={font-size: size, line-height: heading-line-height}>
            {children}
        </tag>
```

## CSS Custom Properties

```css
/* ============================================
   Modular Type Scale — Major Third (1.25)
   Base: 16px (1rem)
   ============================================ */
:root {
  /* Font families — 2 families max */
  --font-heading: 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  /* Scale steps */
  --text-sm:      0.8rem;    /* 12.8px */
  --text-base:    1rem;      /* 16px   */
  --text-lg:      1.25rem;   /* 20px   */
  --text-xl:      1.563rem;  /* 25px   */
  --text-2xl:     1.953rem;  /* 31.25px */
  --text-3xl:     2.441rem;  /* 39.06px */
  --text-display: 3.052rem;  /* 48.83px */

  /* Line heights */
  --leading-tight:   1.2;
  --leading-normal:  1.5;
  --leading-relaxed: 1.6;

  /* Letter spacing */
  --tracking-tight:  -0.02em;
  --tracking-normal:  0;
  --tracking-wide:    0.05em;
  --tracking-caps:    0.1em;
}

/* ============================================
   Heading styles
   ============================================ */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  margin: 0;
}

h1 { font-size: clamp(2rem, 1.5rem + 2vw, var(--text-display)); }
h2 { font-size: clamp(1.5rem, 1.2rem + 1.5vw, var(--text-3xl)); }
h3 { font-size: clamp(1.25rem, 1rem + 1vw, var(--text-2xl)); }
h4 { font-size: var(--text-xl); }
h5 { font-size: var(--text-lg); }
h6 { font-size: var(--text-base); font-weight: 600; }

/* ============================================
   Body and paragraph styles
   ============================================ */
body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  letter-spacing: var(--tracking-normal);
}

/* Constrain line length to 45-75 characters */
p, li, blockquote {
  max-width: 65ch;
}

/* Small/caption text needs more line height */
small, .caption {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

/* ALL CAPS treatment */
.uppercase {
  text-transform: uppercase;
  letter-spacing: var(--tracking-caps);
  line-height: 1.1;
}

/* Code / monospace */
code, pre {
  font-family: var(--font-mono);
  font-size: 0.875em; /* slightly smaller than surrounding text */
}
```

## Tailwind Configuration

```js
// tailwind.config.js
export default {
  theme: {
    fontFamily: {
      heading: ['Inter', 'system-ui', 'sans-serif'],
      body: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
    },
    fontSize: {
      sm:      ['0.8rem',   { lineHeight: '1.6' }],
      base:    ['1rem',     { lineHeight: '1.5' }],
      lg:      ['1.25rem',  { lineHeight: '1.4' }],
      xl:      ['1.563rem', { lineHeight: '1.3' }],
      '2xl':   ['1.953rem', { lineHeight: '1.2' }],
      '3xl':   ['2.441rem', { lineHeight: '1.2' }],
      display: ['3.052rem', { lineHeight: '1.1' }],
    },
  },
};
```

```html
<!-- Usage in Tailwind -->
<h1 class="font-heading text-display tracking-tight">Page Title</h1>
<h2 class="font-heading text-3xl tracking-tight">Section Heading</h2>
<p class="font-body text-base max-w-prose">
  Body text constrained to a readable line length.
</p>
<span class="text-sm uppercase tracking-widest">Label</span>
```

## React

```jsx
const HEADING_STYLES = {
  1: 'text-display font-heading leading-tight tracking-tight',
  2: 'text-3xl font-heading leading-tight tracking-tight',
  3: 'text-2xl font-heading leading-tight tracking-tight',
  4: 'text-xl font-heading leading-snug',
  5: 'text-lg font-heading leading-snug',
  6: 'text-base font-heading font-semibold',
};

function Heading({ level = 2, children, className = '' }) {
  const Tag = `h${level}`;
  const baseStyle = HEADING_STYLES[level] || HEADING_STYLES[2];

  return <Tag className={`${baseStyle} ${className}`}>{children}</Tag>;
}

function Prose({ children }) {
  return (
    <div className="font-body text-base leading-normal max-w-prose">
      {children}
    </div>
  );
}

// Usage
function ArticlePage({ title, subtitle, body }) {
  return (
    <article>
      <Heading level={1}>{title}</Heading>
      <Heading level={2}>{subtitle}</Heading>
      <Prose>{body}</Prose>
    </article>
  );
}
```

## Key Points

- **Major Third (1.25) scale** is the versatile default — enough contrast between levels without extreme jumps
- **`clamp()`** on h1-h3 provides fluid responsive sizing without media queries
- **`max-width: 65ch`** on text elements enforces the 45-75 character line length rule
- **Line height decreases** as font size increases: body 1.5, headings 1.2, display 1.1
- **ALL CAPS text** gets `letter-spacing: 0.1em` to compensate for reduced legibility
- **Single font family** (Inter) with weight variation is the safest approach for applications
- Tailwind `fontSize` config bundles size and line-height together for consistency
