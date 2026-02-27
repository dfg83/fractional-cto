# Design Tokens System

Demonstrates a complete three-layer token architecture (primitive, semantic, component) in CSS custom properties, Tailwind configuration, and a React theme provider.

## Pseudocode

```
// Layer 1: Primitive — raw values, the palette
PRIMITIVES = {
  blue-500: "#3B82F6",  blue-600: "#2563EB",
  gray-50: "#F9FAFB",   gray-100: "#F3F4F6",
  gray-200: "#E5E7EB",  gray-500: "#6B7280",
  gray-700: "#374151",  gray-900: "#111827",
  green-500: "#22C55E", red-500: "#EF4444",
  white: "#FFFFFF",     black: "#000000",
  radius-sm: 4px,       radius-md: 8px,   radius-lg: 12px,
  space-1: 4px,         space-2: 8px,      space-4: 16px,
  space-6: 24px,        space-8: 32px,
  shadow-sm: "0 1px 2px rgba(0,0,0,0.05)",
  shadow-md: "0 4px 6px rgba(0,0,0,0.07)",
}

// Layer 2: Semantic — purpose-named, references primitives
SEMANTIC = {
  color-primary:      PRIMITIVES.blue-500,
  color-primary-hover: PRIMITIVES.blue-600,
  color-bg-page:      PRIMITIVES.gray-50,
  color-bg-surface:   PRIMITIVES.white,
  color-bg-subtle:    PRIMITIVES.gray-100,
  color-text-primary: PRIMITIVES.gray-900,
  color-text-secondary: PRIMITIVES.gray-500,
  color-border:       PRIMITIVES.gray-200,
  color-success:      PRIMITIVES.green-500,
  color-error:        PRIMITIVES.red-500,
  radius-default:     PRIMITIVES.radius-md,
  spacing-element:    PRIMITIVES.space-2,
  spacing-section:    PRIMITIVES.space-8,
}

// Layer 3: Component — scoped, references semantic only
COMPONENT = {
  button-bg:      SEMANTIC.color-primary,
  button-text:    SEMANTIC.color-text-on-primary,
  button-radius:  SEMANTIC.radius-default,
  button-padding: SEMANTIC.spacing-element + " " + SEMANTIC.spacing-section,
  card-bg:        SEMANTIC.color-bg-surface,
  card-border:    SEMANTIC.color-border,
  card-radius:    SEMANTIC.radius-default,
  card-shadow:    SEMANTIC.shadow-default,
  input-bg:       SEMANTIC.color-bg-surface,
  input-border:   SEMANTIC.color-border,
  input-radius:   SEMANTIC.radius-default,
}
```

## CSS Custom Properties

```css
/* ============================================
   LAYER 1: Primitive Tokens
   Raw values. Never reference in components.
   ============================================ */
:root {
  /* Colors */
  --primitive-blue-500:   #3B82F6;
  --primitive-blue-600:   #2563EB;
  --primitive-gray-50:    #F9FAFB;
  --primitive-gray-100:   #F3F4F6;
  --primitive-gray-200:   #E5E7EB;
  --primitive-gray-500:   #6B7280;
  --primitive-gray-700:   #374151;
  --primitive-gray-900:   #111827;
  --primitive-green-500:  #22C55E;
  --primitive-red-500:    #EF4444;
  --primitive-white:      #FFFFFF;

  /* Radius */
  --primitive-radius-sm:  4px;
  --primitive-radius-md:  8px;
  --primitive-radius-lg:  12px;
  --primitive-radius-full: 9999px;

  /* Spacing */
  --primitive-space-1:  4px;
  --primitive-space-2:  8px;
  --primitive-space-3:  12px;
  --primitive-space-4:  16px;
  --primitive-space-6:  24px;
  --primitive-space-8:  32px;
  --primitive-space-12: 48px;

  /* Elevation */
  --primitive-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --primitive-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --primitive-shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Motion */
  --primitive-duration-fast:   100ms;
  --primitive-duration-normal: 200ms;
  --primitive-duration-slow:   300ms;
}

/* ============================================
   LAYER 2: Semantic Tokens
   Purpose-named. These change between themes.
   ============================================ */
:root {
  --color-primary:        var(--primitive-blue-500);
  --color-primary-hover:  var(--primitive-blue-600);
  --color-bg-page:        var(--primitive-gray-50);
  --color-bg-surface:     var(--primitive-white);
  --color-bg-subtle:      var(--primitive-gray-100);
  --color-text-primary:   var(--primitive-gray-900);
  --color-text-secondary: var(--primitive-gray-500);
  --color-text-tertiary:  var(--primitive-gray-500);
  --color-border-default: var(--primitive-gray-200);
  --color-status-success: var(--primitive-green-500);
  --color-status-error:   var(--primitive-red-500);

  --radius-default:       var(--primitive-radius-md);
  --radius-pill:          var(--primitive-radius-full);
  --shadow-default:       var(--primitive-shadow-sm);
  --color-text-on-primary: var(--primitive-white);

  --spacing-padding-x:    var(--primitive-space-6);
  --spacing-padding-y:    var(--primitive-space-3);

  --duration-interaction: var(--primitive-duration-fast);
  --duration-transition:  var(--primitive-duration-normal);
}

/* Dark theme — only semantic tokens change */
[data-theme="dark"] {
  --color-bg-page:        var(--primitive-gray-900);
  --color-bg-surface:     var(--primitive-gray-700);
  --color-bg-subtle:      oklch(0.25 0.00 0);
  --color-text-primary:   var(--primitive-gray-50);
  --color-text-secondary: var(--primitive-gray-200);
  --color-border-default: var(--primitive-gray-700);
}

/* ============================================
   LAYER 3: Component Tokens
   Scoped. Reference semantic tokens only.
   ============================================ */
:root {
  /* Button */
  --button-bg:           var(--color-primary);
  --button-bg-hover:     var(--color-primary-hover);
  --button-text:         var(--color-text-on-primary);
  --button-radius:       var(--radius-default);
  --button-padding-x:    var(--spacing-padding-x);
  --button-padding-y:    var(--spacing-padding-y);

  /* Card */
  --card-bg:             var(--color-bg-surface);
  --card-border:         var(--color-border-default);
  --card-radius:         var(--radius-default);
  --card-padding:        var(--spacing-padding-x);
  --card-shadow:         var(--shadow-default);

  /* Input */
  --input-bg:            var(--color-bg-surface);
  --input-border:        var(--color-border-default);
  --input-border-focus:  var(--color-primary);
  --input-border-error:  var(--color-status-error);
  --input-radius:        var(--radius-default);
  --input-padding:       var(--spacing-padding-y) var(--spacing-padding-x);
}

/* Components use their own tokens — clean and predictable */
.button {
  background: var(--button-bg);
  color: var(--button-text);
  padding: var(--button-padding-y) var(--button-padding-x);
  border-radius: var(--button-radius);
  border: none;
  transition: background var(--duration-interaction) ease;
}

.button:hover {
  background: var(--button-bg-hover);
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--card-shadow);
}

.input {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--input-radius);
  padding: var(--input-padding);
  color: var(--color-text-primary);
  transition: border-color var(--duration-interaction) ease;
}

.input:focus {
  border-color: var(--input-border-focus);
  outline: none;
}
```

## Tailwind Config

```js
// tailwind.config.js — tokens as Tailwind theme values
module.exports = {
  theme: {
    colors: {
      primary:   'var(--color-primary)',
      'primary-hover': 'var(--color-primary-hover)',
      'bg-page':    'var(--color-bg-page)',
      'bg-surface': 'var(--color-bg-surface)',
      'bg-subtle':  'var(--color-bg-subtle)',
      'text-primary':   'var(--color-text-primary)',
      'text-secondary': 'var(--color-text-secondary)',
      'border-default': 'var(--color-border-default)',
      success: 'var(--color-status-success)',
      error:   'var(--color-status-error)',
    },
    spacing: {
      1: 'var(--primitive-space-1)',
      2: 'var(--primitive-space-2)',
      3: 'var(--primitive-space-3)',
      4: 'var(--primitive-space-4)',
      6: 'var(--primitive-space-6)',
      8: 'var(--primitive-space-8)',
      12: 'var(--primitive-space-12)',
    },
    borderRadius: {
      sm:   'var(--primitive-radius-sm)',
      DEFAULT: 'var(--radius-default)',
      lg:   'var(--primitive-radius-lg)',
      full: 'var(--primitive-radius-full)',
    },
    boxShadow: {
      sm: 'var(--primitive-shadow-sm)',
      md: 'var(--primitive-shadow-md)',
      lg: 'var(--primitive-shadow-lg)',
    },
  },
};
```

## React Theme Provider

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

/* Token values defined in CSS — React manages theme switching only */
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggle = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  return useContext(ThemeContext);
}

/* Components use CSS token classes — no inline theme logic */
function Button({ variant = 'primary', children, ...props }) {
  const styles = {
    primary: 'button',
    outlined: 'button button--outlined',
    ghost: 'button button--ghost',
  };

  return (
    <button className={styles[variant]} {...props}>
      {children}
    </button>
  );
}

function Card({ children }) {
  return <div className="card">{children}</div>;
}
```

## Key Points

- **Three layers, strict references**: primitives -> semantic -> component, never skip a layer
- **Theme switching changes only semantic tokens**: dark mode overrides `[data-theme="dark"]`, all components update automatically
- **Constrained sets**: 11 colors, 7 spacing values, 4 radii, 3 shadows, 3 motion durations -- well within recommended limits
- **Tailwind bridges to CSS tokens**: `var()` references in tailwind.config.js keep one source of truth
- **React manages theme state, CSS manages visuals**: no inline color logic in components
- **Component tokens scope decisions**: `--button-bg` is more maintainable than `var(--color-primary)` repeated in every button variant
