# Quickstart: Dark Theme Implementation

**Feature**: 005-dark-todo-ui
**Date**: 2026-01-15

## Prerequisites

- Node.js 18+ installed
- Existing frontend running (`npm run dev` in frontend/)
- Backend API running on port 8000

## Implementation Steps

### Step 1: Update Tailwind Configuration

Edit `frontend/tailwind.config.ts`:

```typescript
const config: Config = {
  content: [...],
  theme: {
    extend: {
      colors: {
        // Dark theme base
        dark: '#0F1115',
        surface: '#1A1D23',

        // Primary accent - Teal
        primary: {
          DEFAULT: '#2DD4BF',
          hover: '#14B8A6',
          50: '#F0FDFA',
          // ... keep existing shades for compatibility
        },

        // Secondary accent - Amber
        secondary: {
          DEFAULT: '#FBBF24',
          hover: '#F59E0B',
        },

        // Status colors
        success: {
          DEFAULT: '#22C55E',
          // ... existing shades
        },
        danger: {
          DEFAULT: '#EF4444',
          // ... existing shades
        },

        // Text colors
        light: '#E5E7EB',
        muted: '#9CA3AF',
      },
    },
  },
};
```

### Step 2: Update Global Styles

Edit `frontend/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-dark text-light antialiased;
  }
}
```

### Step 3: Update Root Layout

Edit `frontend/app/layout.tsx`:

```tsx
<body className={`${inter.className} antialiased bg-dark text-light`}>
```

### Step 4: Update Component Classes

For each component, replace:
- `bg-white` → `bg-surface`
- `bg-gray-50` → `bg-dark`
- `text-gray-900` → `text-light`
- `text-gray-500` → `text-muted`
- `border-gray-200` → `border-white/10`
- `focus:ring-primary-500` → `focus:ring-primary`

### Step 5: Update Button Variants

```tsx
const variants = {
  primary: "bg-secondary text-dark hover:bg-secondary-hover",
  secondary: "bg-surface text-light border border-white/10 hover:bg-white/5",
  destructive: "bg-danger text-white hover:bg-danger/90",
  ghost: "text-light hover:bg-white/5",
  link: "text-primary underline-offset-4 hover:underline",
};
```

### Step 6: Update Status Badges

```tsx
// Pending badge
<span className="bg-secondary/20 text-secondary px-2 py-0.5 rounded-full text-xs">
  Pending
</span>

// Completed badge
<span className="bg-success/20 text-success px-2 py-0.5 rounded-full text-xs">
  Completed
</span>
```

### Step 7: Update Navigation

```tsx
// Active nav link
<Link className="text-primary border-b-2 border-primary">
  Dashboard
</Link>

// Inactive nav link
<Link className="text-muted hover:text-light">
  Tasks
</Link>
```

## Verification Checklist

- [ ] Background is near-black (#0F1115)
- [ ] Cards have charcoal surface (#1A1D23)
- [ ] Focus states show teal ring (#2DD4BF)
- [ ] Primary buttons are amber (#FBBF24)
- [ ] Pending badges are amber
- [ ] Completed badges are green (#22C55E)
- [ ] Text is readable (light gray on dark)
- [ ] Navigation shows teal active indicator
- [ ] No light theme elements remaining

## Testing

1. Start the dev server: `npm run dev`
2. Open http://localhost:3000
3. Verify dark theme on:
   - Login page
   - Signup page
   - Dashboard
   - Task list
   - Task creation form
4. Check responsive behavior at 320px, 768px, 1024px, 1920px
5. Verify focus states on all inputs and buttons
6. Verify status badge colors on tasks
