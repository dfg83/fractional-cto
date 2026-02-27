# Color System and Dark Mode

Demonstrates building a complete HSL-based color system with shade scale generation, semantic tokens, and dark mode implementation.

## Pseudocode

```
function generateShadeScale(hue, baseSaturation):
    return:
        50:  hsl(hue, baseSaturation - 15%, 96%)
        100: hsl(hue, baseSaturation - 10%, 91%)
        200: hsl(hue, baseSaturation - 5%,  83%)
        300: hsl(hue, baseSaturation,       73%)
        400: hsl(hue, baseSaturation,       60%)
        500: hsl(hue, baseSaturation,       48%)    // base
        600: hsl(hue, baseSaturation,       40%)    // hover
        700: hsl(hue, baseSaturation,       30%)    // pressed
        800: hsl(hue, baseSaturation - 5%,  22%)
        900: hsl(hue, baseSaturation - 10%, 13%)

config ColorSystem:
    brand:   generateShadeScale(220, 65%)
    neutral: generateShadeScale(220, 10%)
    semantic:
        success: hsl(145, 60%, 42%)
        warning: hsl(40, 90%, 50%)
        error:   hsl(4, 72%, 50%)
        info:    hsl(210, 70%, 50%)

    darkMode:
        swap backgrounds: neutral-900 -> bg, neutral-50 -> text
        reduce saturation: -15% on all brand colors
        reduce white opacity: 87%
```

## CSS Custom Properties

```css
/* ============================================
   Brand Shade Scale — HSL with systematic lightness
   Hue: 220 (blue), Saturation: 65% base
   ============================================ */
:root {
  --brand-50:  hsl(220, 50%, 96%);
  --brand-100: hsl(220, 55%, 91%);
  --brand-200: hsl(220, 60%, 83%);
  --brand-300: hsl(220, 65%, 73%);
  --brand-400: hsl(220, 65%, 60%);
  --brand-500: hsl(220, 65%, 48%);
  --brand-600: hsl(220, 65%, 40%);
  --brand-700: hsl(220, 65%, 30%);
  --brand-800: hsl(220, 60%, 22%);
  --brand-900: hsl(220, 55%, 13%);

  /* Neutral Scale — brand-tinted gray (not pure gray) */
  --neutral-50:  hsl(220, 10%, 97%);
  --neutral-100: hsl(220, 10%, 92%);
  --neutral-200: hsl(220, 10%, 85%);
  --neutral-300: hsl(220, 8%, 73%);
  --neutral-400: hsl(220, 8%, 55%);
  --neutral-500: hsl(220, 8%, 42%);
  --neutral-600: hsl(220, 10%, 33%);
  --neutral-700: hsl(220, 12%, 25%);
  --neutral-800: hsl(220, 14%, 16%);
  --neutral-900: hsl(220, 15%, 10%);

  /* Semantic Colors */
  --success-500: hsl(145, 60%, 42%);
  --success-100: hsl(145, 50%, 90%);
  --warning-500: hsl(40, 90%, 50%);
  --warning-100: hsl(40, 80%, 90%);
  --error-500:   hsl(4, 72%, 50%);
  --error-100:   hsl(4, 60%, 92%);
  --info-500:    hsl(210, 70%, 50%);
  --info-100:    hsl(210, 60%, 92%);
}

/* ============================================
   Semantic Tokens — Light Mode (60-30-10)
   ============================================ */
:root {
  /* 60% — Dominant (backgrounds, surfaces) */
  --color-bg-page:    var(--neutral-50);
  --color-bg-surface: hsl(0, 0%, 100%);
  --color-bg-subtle:  var(--neutral-100);

  /* 30% — Secondary (cards, borders, secondary text) */
  --color-border:        var(--neutral-200);
  --color-text-secondary: var(--neutral-500);

  /* 10% — Accent (CTAs, active states, links) */
  --color-accent:       var(--brand-500);
  --color-accent-hover: var(--brand-600);

  /* Text */
  --color-text-primary: var(--neutral-900);

  /* Semantic */
  --color-success:    var(--success-500);
  --color-success-bg: var(--success-100);
  --color-warning:    var(--warning-500);
  --color-warning-bg: var(--warning-100);
  --color-error:      var(--error-500);
  --color-error-bg:   var(--error-100);
  --color-info:       var(--info-500);
  --color-info-bg:    var(--info-100);
}

/* ============================================
   Dark Mode — NOT an inversion
   ============================================ */
[data-theme="dark"] {
  /* Backgrounds: dark grays, not pure black */
  --color-bg-page:    var(--neutral-900);
  --color-bg-surface: var(--neutral-800);
  --color-bg-subtle:  var(--neutral-700);

  /* Borders: lighter in dark mode */
  --color-border: var(--neutral-600);

  /* Text: reduced opacity, not pure white */
  --color-text-primary:   hsl(220, 10%, 90%);
  --color-text-secondary: var(--neutral-400);

  /* Accent: reduce saturation for dark backgrounds */
  --color-accent:       hsl(220, 50%, 58%);
  --color-accent-hover: hsl(220, 50%, 65%);

  /* Semantic: lighten for contrast on dark backgrounds */
  --color-success:    hsl(145, 50%, 55%);
  --color-success-bg: hsl(145, 30%, 18%);
  --color-warning:    hsl(40, 80%, 60%);
  --color-warning-bg: hsl(40, 40%, 18%);
  --color-error:      hsl(4, 62%, 60%);
  --color-error-bg:   hsl(4, 35%, 18%);
  --color-info:       hsl(210, 60%, 60%);
  --color-info-bg:    hsl(210, 35%, 18%);
}
```

## Tailwind Configuration

```js
// tailwind.config.js
export default {
  theme: {
    colors: {
      brand: {
        50:  'hsl(220, 50%, 96%)',
        100: 'hsl(220, 55%, 91%)',
        200: 'hsl(220, 60%, 83%)',
        300: 'hsl(220, 65%, 73%)',
        400: 'hsl(220, 65%, 60%)',
        500: 'hsl(220, 65%, 48%)',
        600: 'hsl(220, 65%, 40%)',
        700: 'hsl(220, 65%, 30%)',
        800: 'hsl(220, 60%, 22%)',
        900: 'hsl(220, 55%, 13%)',
      },
      neutral: {
        50:  'hsl(220, 10%, 97%)',
        100: 'hsl(220, 10%, 92%)',
        200: 'hsl(220, 10%, 85%)',
        300: 'hsl(220, 8%, 73%)',
        400: 'hsl(220, 8%, 55%)',
        500: 'hsl(220, 8%, 42%)',
        600: 'hsl(220, 10%, 33%)',
        700: 'hsl(220, 12%, 25%)',
        800: 'hsl(220, 14%, 16%)',
        900: 'hsl(220, 15%, 10%)',
      },
      success: { DEFAULT: 'hsl(145, 60%, 42%)', light: 'hsl(145, 50%, 90%)' },
      warning: { DEFAULT: 'hsl(40, 90%, 50%)',  light: 'hsl(40, 80%, 90%)' },
      error:   { DEFAULT: 'hsl(4, 72%, 50%)',   light: 'hsl(4, 60%, 92%)' },
      info:    { DEFAULT: 'hsl(210, 70%, 50%)', light: 'hsl(210, 60%, 92%)' },
    },
  },
};
```

```html
<!-- Semantic alert using the color system -->
<div class="rounded-md border border-error/20 bg-error-light p-4">
  <p class="text-sm font-medium text-error">Upload failed. File exceeds 10MB limit.</p>
</div>

<!-- Success banner -->
<div class="rounded-md border border-success/20 bg-success-light p-4">
  <p class="text-sm font-medium text-success">Changes saved successfully.</p>
</div>
```

## React

```jsx
const SEMANTIC_STYLES = {
  success: {
    container: 'bg-success-light border-success/20 text-success',
    icon: 'text-success',
  },
  warning: {
    container: 'bg-warning-light border-warning/20 text-warning',
    icon: 'text-warning',
  },
  error: {
    container: 'bg-error-light border-error/20 text-error',
    icon: 'text-error',
  },
  info: {
    container: 'bg-info-light border-info/20 text-info',
    icon: 'text-info',
  },
};

function Alert({ variant = 'info', icon: Icon, children }) {
  const styles = SEMANTIC_STYLES[variant];

  return (
    <div className={`flex items-start gap-3 rounded-md border p-4 ${styles.container}`}
         role="alert">
      {Icon && <Icon className={`h-5 w-5 shrink-0 ${styles.icon}`} />}
      <p className="text-sm font-medium">{children}</p>
    </div>
  );
}

// Dark mode toggle using data attribute
function ThemeToggle() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem('theme') === 'dark'
      || (!localStorage.getItem('theme')
          && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <button onClick={() => setIsDark((prev) => !prev)}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
      {isDark ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
```

## Key Points

- **HSL shade scale** is generated by fixing hue and varying lightness systematically — no manual color picking
- **Saturation decreases at extremes** (50, 100, 800, 900) to avoid garish tints and murky darks
- **Neutral grays are brand-tinted** (hue 220 at 8-15% saturation) for subtle cohesion
- **Dark mode is not inversion** — it uses dedicated dark gray values, reduced saturation on accents, and adjusted semantic colors
- **Semantic tokens** reference the shade scale — theme switching only changes semantic values, not component code
- **60-30-10 distribution** is enforced by making 60% backgrounds neutral, 30% borders/cards subdued, 10% accents saturated
- Always test contrast ratios against WCAG AA: 4.5:1 for body text, 3:1 for large text
