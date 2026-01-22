# Research: Dark Theme Todo Web App UI

**Feature**: 005-dark-todo-ui
**Date**: 2026-01-15

## Research Questions

### 1. Dark Theme Color Contrast Requirements

**Decision**: Use WCAG 2.1 AA standard (4.5:1 contrast ratio for text)

**Rationale**:
- #E5E7EB (light gray text) on #0F1115 (dark background) = ~13:1 contrast ratio (PASS)
- #9CA3AF (muted text) on #0F1115 = ~7:1 contrast ratio (PASS)
- #2DD4BF (teal) on #0F1115 = ~9:1 contrast ratio (PASS)
- #FBBF24 (amber) on #0F1115 = ~11:1 contrast ratio (PASS)

**Alternatives considered**:
- Pure black (#000000) background - rejected, too harsh
- Darker surface (#111111) - rejected, insufficient contrast between background and cards

### 2. Tailwind Dark Color Configuration

**Decision**: Extend Tailwind config with custom color tokens instead of using dark: prefix

**Rationale**:
- Simpler implementation - no conditional dark: classes needed
- Consistent with single-theme approach (no theme switching)
- Better readability in component code

**Alternatives considered**:
- Use Tailwind dark mode with dark: prefix - rejected, adds complexity for single-theme app
- CSS variables only - rejected, loses Tailwind's utility benefits

### 3. Input Focus States on Dark Background

**Decision**: Use teal (#2DD4BF) ring with 2px width and slight glow effect

**Rationale**:
- High visibility on dark background
- Consistent with primary accent color
- Provides clear accessibility indicator

**Alternatives considered**:
- Amber focus rings - rejected, conflicts with button colors
- White focus rings - rejected, too harsh on dark background

### 4. Status Badge Implementation

**Decision**: Use pill-shaped badges with amber (pending) and green (completed)

**Rationale**:
- Clear visual distinction at a glance
- Follows established UX patterns for status indicators
- Specified colors in requirements

**Alternatives considered**:
- Icon-only status - rejected, less accessible
- Checkbox styling - already implemented in task-item, badges add clarity

### 5. Navigation Active State

**Decision**: Use teal underline/border-bottom for active navigation items

**Rationale**:
- Clear indicator visible against dark background
- Consistent with primary accent color
- Non-intrusive, modern SaaS pattern

**Alternatives considered**:
- Background highlight - rejected, disrupts clean nav appearance
- Text color change only - rejected, insufficient visibility

### 6. Card Shadows on Dark Background

**Decision**: Use subtle borders instead of shadows for card definition

**Rationale**:
- Shadows are less visible on dark backgrounds
- Subtle border (border-white/5 or border-white/10) provides definition
- Cleaner dark theme aesthetic

**Alternatives considered**:
- Strong drop shadows - rejected, doesn't work well on dark
- No definition - rejected, cards blend into background

### 7. Button Hierarchy

**Decision**:
- Primary action: Amber (#FBBF24) background with dark text
- Secondary action: Surface (#1A1D23) background with light border
- Destructive: Red (#EF4444) background

**Rationale**:
- Amber stands out clearly for primary CTAs
- Maintains visual hierarchy
- Consistent with pending status color

**Alternatives considered**:
- Teal primary buttons - rejected, conflicts with focus states
- Ghost buttons only - rejected, insufficient CTA visibility

## Implementation Notes

### Tailwind Config Color Tokens

```javascript
colors: {
  dark: '#0F1115',
  surface: '#1A1D23',
  primary: {
    DEFAULT: '#2DD4BF',
    hover: '#14B8A6',
  },
  secondary: {
    DEFAULT: '#FBBF24',
    hover: '#F59E0B',
  },
  success: '#22C55E',
  danger: '#EF4444',
  light: '#E5E7EB',
  muted: '#9CA3AF',
}
```

### Component Color Mapping

| Component | Current Classes | New Classes |
|-----------|-----------------|-------------|
| Body | bg-gray-50 text-gray-900 | bg-dark text-light |
| Card | bg-white border-gray-200 | bg-surface border-white/10 |
| Button Primary | bg-primary-600 | bg-secondary text-dark |
| Button Secondary | bg-gray-100 | bg-surface border-white/10 |
| Input | border-gray-300 focus:ring-primary-500 | border-white/20 focus:ring-primary |
| Nav Active | text-primary-600 | text-primary border-b-primary |
| Badge Pending | bg-amber-100 text-amber-800 | bg-secondary/20 text-secondary |
| Badge Complete | bg-green-100 text-green-800 | bg-success/20 text-success |
