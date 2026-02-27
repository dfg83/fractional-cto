# Accessible Form with Labels, Focus Indicators, and Error Messaging

Demonstrates an accessible form with visible labels, custom focus indicators using `:focus-visible`, inline error messaging with ARIA attributes, and keyboard-navigable structure.

## Pseudocode

```
component AccessibleForm(fields, onSubmit):
    state errors = {}

    validate(field):
        if field.required and field.value is empty:
            errors[field.name] = "#{field.label} is required"
        if field.type is "email" and not valid_email(field.value):
            errors[field.name] = "Email must include @ and a domain"

    render:
        <form onSubmit={onSubmit} noValidate>
            <a href="#main" class="skip-link">Skip to content</a>

            for field in fields:
                <div class="field" aria-invalid={errors[field.name] ? "true" : "false"}>
                    <label for={field.name}>{field.label}</label>
                    <input
                        id={field.name}
                        type={field.type}
                        required={field.required}
                        aria-describedby={errors[field.name] ? "#{field.name}-error" : null}
                    />
                    if errors[field.name]:
                        <p id="#{field.name}-error" role="alert">{errors[field.name]}</p>
                </div>

            <button type="submit">Submit</button>
        </form>
```

## CSS/HTML

```html
<style>
/* ============================================
   Skip Link (visible on focus only)
   ============================================ */
.skip-link {
  position: absolute;
  top: -100%;
  left: 16px;
  padding: 8px 16px;
  background: var(--color-primary, #2563eb);
  color: #fff;
  font-weight: 600;
  border-radius: 4px;
  z-index: 9999;
  text-decoration: none;
}

.skip-link:focus {
  top: 16px;
}

/* ============================================
   Focus Indicators
   ============================================ */
*:focus-visible {
  outline: 3px solid var(--color-focus, #2563eb);
  outline-offset: 2px;
}

/* Remove default focus for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}

/* ============================================
   Form Field Layout
   ============================================ */
.form-group {
  margin-bottom: 24px; /* external spacing between fields */
}

.form-group label {
  display: block;
  margin-bottom: 4px; /* tight label-to-input proximity */
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary, #1e293b);
}

.form-group input {
  display: block;
  width: 100%;
  padding: 10px 12px;
  font-size: 1rem;
  border: 1px solid var(--color-border-default, #cbd5e1);
  border-radius: 6px;
  background: var(--color-bg-surface, #fff);
  color: var(--color-text-primary, #1e293b);
  min-height: 44px; /* touch target minimum */
}

/* ============================================
   Error State
   ============================================ */
.form-group[aria-invalid="true"] input {
  border-color: var(--color-error, #dc2626);
  border-width: 2px;
}

.form-group[aria-invalid="true"] label {
  color: var(--color-error, #dc2626);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 0.8125rem;
  color: var(--color-error, #dc2626);
}

.error-message::before {
  content: "⚠";  /* redundant encoding: color + icon + text */
}

/* ============================================
   Submit Button
   ============================================ */
.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  min-width: 44px;
  padding: 10px 24px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: var(--color-primary, #2563eb);
  color: #fff;
  cursor: pointer;
}
</style>

<a href="#main" class="skip-link">Skip to main content</a>

<main id="main">
  <form novalidate>
    <div class="form-group" aria-invalid="false">
      <label for="fullName">Full Name</label>
      <input
        id="fullName"
        name="fullName"
        type="text"
        required
        autocomplete="name"
      />
    </div>

    <div class="form-group" aria-invalid="true">
      <label for="email">Email Address</label>
      <input
        id="email"
        name="email"
        type="email"
        required
        autocomplete="email"
        aria-describedby="email-error"
      />
      <p id="email-error" class="error-message" role="alert">
        Email must include @ and a domain (e.g., user@example.com)
      </p>
    </div>

    <div class="form-group" aria-invalid="false">
      <label for="message">Message</label>
      <textarea
        id="message"
        name="message"
        rows="4"
        style="width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem;"
      ></textarea>
    </div>

    <button type="submit" class="btn-submit">Send Message</button>
  </form>
</main>
```

## Tailwind

```html
<!-- Skip link -->
<a
  href="#main"
  class="absolute -top-full left-4 z-50 rounded bg-blue-600 px-4 py-2 font-semibold text-white focus:top-4"
>
  Skip to main content
</a>

<main id="main" class="mx-auto max-w-lg p-6">
  <form novalidate>
    <!-- Valid field -->
    <div class="mb-6">
      <label for="fullName" class="mb-1 block text-sm font-semibold text-gray-900">
        Full Name
      </label>
      <input
        id="fullName"
        name="fullName"
        type="text"
        required
        autocomplete="name"
        class="block w-full rounded-md border border-gray-300 px-3 py-2.5 text-base
               focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2
               focus-visible:outline-blue-600"
      />
    </div>

    <!-- Invalid field with error -->
    <div class="mb-6" aria-invalid="true">
      <label for="email" class="mb-1 block text-sm font-semibold text-red-600">
        Email Address
      </label>
      <input
        id="email"
        name="email"
        type="email"
        required
        autocomplete="email"
        aria-describedby="email-error"
        class="block w-full rounded-md border-2 border-red-600 px-3 py-2.5 text-base
               focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2
               focus-visible:outline-blue-600"
      />
      <p id="email-error" class="mt-1 flex items-center gap-1 text-sm text-red-600" role="alert">
        <span aria-hidden="true">⚠</span>
        Email must include @ and a domain (e.g., user@example.com)
      </p>
    </div>

    <button
      type="submit"
      class="inline-flex min-h-[44px] items-center rounded-md bg-blue-600 px-6 py-2.5
             font-semibold text-white hover:bg-blue-700
             focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2
             focus-visible:outline-blue-600"
    >
      Send Message
    </button>
  </form>
</main>
```

## React

```jsx
import { useState, useRef, useId } from 'react';

function AccessibleForm() {
  const [errors, setErrors] = useState({});
  const formRef = useRef(null);
  const emailId = useId();
  const nameId = useId();

  function validate(formData) {
    const newErrors = {};

    if (!formData.get('fullName')?.trim()) {
      newErrors.fullName = 'Full Name is required';
    }

    const email = formData.get('email')?.trim();
    if (!email) {
      newErrors.email = 'Email Address is required';
    } else if (!email.includes('@') || !email.includes('.')) {
      newErrors.email = 'Email must include @ and a domain (e.g., user@example.com)';
    }

    return newErrors;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const newErrors = validate(formData);
    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      /* Move focus to first error field */
      const firstErrorField = Object.keys(newErrors)[0];
      formRef.current?.querySelector(`[name="${firstErrorField}"]`)?.focus();
    }
  }

  return (
    <>
      <a href="#main" className="skip-link">
        Skip to main content
      </a>

      <main id="main">
        <form ref={formRef} onSubmit={handleSubmit} noValidate>
          <FormField
            id={nameId}
            label="Full Name"
            name="fullName"
            type="text"
            required
            autoComplete="name"
            error={errors.fullName}
          />

          <FormField
            id={emailId}
            label="Email Address"
            name="email"
            type="email"
            required
            autoComplete="email"
            error={errors.email}
          />

          <button type="submit" className="btn-submit">
            Send Message
          </button>
        </form>
      </main>
    </>
  );
}

function FormField({ id, label, name, type, required, autoComplete, error }) {
  const errorId = `${id}-error`;
  const hasError = Boolean(error);

  return (
    <div className="form-group" aria-invalid={hasError}>
      <label htmlFor={id} style={{ color: hasError ? 'var(--color-error)' : undefined }}>
        {label}
      </label>
      <input
        id={id}
        name={name}
        type={type}
        required={required}
        autoComplete={autoComplete}
        aria-describedby={hasError ? errorId : undefined}
        style={{
          borderColor: hasError ? 'var(--color-error)' : undefined,
          borderWidth: hasError ? '2px' : undefined,
        }}
      />
      {hasError && (
        <p id={errorId} className="error-message" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
```

## Key Points

- **Skip link** is the first focusable element, hidden until focused -- keyboard users can bypass navigation
- **`:focus-visible`** shows focus rings for keyboard users only, preventing visual noise on mouse clicks
- **Focus ring spec**: 3px solid, 2px offset, high-contrast color -- visible on all backgrounds
- **Labels are visible** and associated via `for`/`id` -- never placeholder-only
- **Label-to-input gap** (4px) is much smaller than **field-to-field gap** (24px) -- Gestalt proximity makes form structure scannable
- **Error messages** use three redundant channels: color (red) + icon (warning symbol) + descriptive text -- accessible to colorblind users
- **`aria-describedby`** links error messages to their inputs -- screen readers announce the error when the field is focused
- **`role="alert"`** on error messages triggers immediate screen reader announcement
- **Touch targets** are 44px minimum height on all interactive elements
- **Focus moves to first error field** on failed submission -- keyboard users are not stranded
