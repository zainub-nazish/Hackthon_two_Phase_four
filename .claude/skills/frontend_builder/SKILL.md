---
name: frontend-skill
description: Build frontend pages, reusable components, layouts, and styling for modern web applications.
---

# Frontend Skill – Pages, Components & Styling

## Instructions

1. **Page Building**
   - Create clear, well-structured pages
   - Follow routing conventions of the framework
   - Separate page-level logic from UI components
   - Ensure SEO-friendly structure where applicable

2. **Component Development**
   - Build reusable, composable components
   - Use props and state appropriately
   - Keep components small and focused
   - Follow consistent naming conventions

3. **Layout Structure**
   - Design responsive layouts (mobile, tablet, desktop)
   - Use layout components for shared UI
   - Maintain consistent spacing and alignment
   - Apply proper visual hierarchy

4. **Styling**
   - Use modern CSS approaches (CSS Modules, Tailwind, styled-components)
   - Ensure accessibility (contrast, focus states)
   - Maintain design consistency
   - Avoid inline styles for scalable systems

5. **Responsiveness & UX**
   - Mobile-first design approach
   - Test across screen sizes
   - Handle loading, empty, and error states gracefully
   - Ensure smooth interactions

## Best Practices
- Keep UI consistent across pages
- Reuse components instead of duplicating code
- Use semantic HTML elements
- Follow accessibility standards (ARIA when needed)
- Optimize for maintainability and scalability

## Example Structure
```tsx
// Layout component
export default function MainLayout({ children }) {
  return (
    <div className="layout">
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  );
}
