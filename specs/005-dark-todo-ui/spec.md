# Feature Specification: Dark Theme Todo Web App UI

**Feature Branch**: `005-dark-todo-ui`
**Created**: 2026-01-15
**Status**: Draft
**Input**: Frontend UI Specification for a modern, dark, distraction-free task management UI

## Overview

Design and implement a modern, dark-themed, distraction-free task management UI for the existing multi-user Todo application. The UI must support task creation, status visibility, and per-user isolation with a unique color palette featuring teal and amber accents on a near-black background.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Dashboard with Dark Theme (Priority: P1)

A user opens the application and sees a visually appealing dark-themed dashboard with clear navigation, a welcoming header, and organized content cards for task management and AI assistance.

**Why this priority**: First impression matters - the dashboard is the entry point and establishes the visual identity of the application.

**Independent Test**: Can be tested by loading the dashboard and verifying all UI elements render with correct dark theme colors and layout.

**Acceptance Scenarios**:

1. **Given** a user navigates to the dashboard, **When** the page loads, **Then** they see a near-black background (#0F1115) with properly contrasted elements
2. **Given** a user is on the dashboard, **When** they view the header, **Then** they see "Manage Your Tasks" title with "Plan, track, and complete efficiently" subtitle centered
3. **Given** a user views the navigation, **When** they hover over menu items, **Then** the active item shows a teal indicator (#2DD4BF)

---

### User Story 2 - Create Task with Dark Form UI (Priority: P1)

A user creates a new task using the dark-themed task creation card with clear input fields, proper focus states, and visual feedback during submission.

**Why this priority**: Core functionality - users must be able to create tasks with a pleasant, accessible dark UI experience.

**Independent Test**: Can be tested by filling out the task form and submitting, verifying visual states and feedback.

**Acceptance Scenarios**:

1. **Given** a user is on the dashboard, **When** they view the task creation card, **Then** they see a charcoal surface (#1A1D23) with teal focus rings on inputs
2. **Given** a user clicks on the title input, **When** the input receives focus, **Then** it displays a teal border/ring (#2DD4BF)
3. **Given** a user enters a valid title, **When** they click "Create Task", **Then** the button shows amber color (#FBBF24) and loading state during submission
4. **Given** the title field is empty, **When** user attempts to submit, **Then** the Create Task button remains disabled

---

### User Story 3 - View Task Status with Visual Badges (Priority: P1)

A user views their tasks with clear status indication using color-coded badges that provide instant visual feedback.

**Why this priority**: Status visibility is essential for task management - users need to quickly identify task states.

**Independent Test**: Can be tested by viewing tasks with different statuses and verifying badge colors.

**Acceptance Scenarios**:

1. **Given** a user has pending tasks, **When** they view the task list, **Then** pending tasks display an amber badge (#FBBF24)
2. **Given** a user has completed tasks, **When** they view the task list, **Then** completed tasks display a green badge (#22C55E)
3. **Given** a user completes a task, **When** the status changes, **Then** the badge color transitions smoothly from amber to green

---

### User Story 4 - Navigate with Dark Top Navigation (Priority: P2)

A user navigates between different sections of the application using the dark-themed top navigation bar with clear active state indicators.

**Why this priority**: Navigation enables access to all features but dashboard is the primary landing point.

**Independent Test**: Can be tested by clicking navigation links and verifying active states and routing.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** they view the navigation bar, **Then** they see "Task Management" app name on the left with Dashboard, Tasks, AI Assistant links
2. **Given** a user clicks on a navigation link, **When** the page changes, **Then** the active link shows a teal underline/indicator
3. **Given** a user is logged in, **When** they view the navigation, **Then** they see their user info and Logout option on the right

---

### User Story 5 - Access AI Assistant Card (Priority: P3)

A user sees an AI Assistant card on the dashboard that provides natural-language task help with a clear call-to-action.

**Why this priority**: AI assistance is an enhancement feature, not core to task management.

**Independent Test**: Can be tested by viewing the AI card and clicking the CTA button.

**Acceptance Scenarios**:

1. **Given** a user is on the dashboard, **When** they view the AI Assistant card, **Then** they see a dark teal surface with rounded corners and soft shadow
2. **Given** a user reads the AI card, **When** they want to use it, **Then** they see an "Open AI Assistant" button as the CTA

---

### User Story 6 - Authenticated User Experience (Priority: P2)

A user without authentication is prompted to log in, and authenticated users only see their own tasks.

**Why this priority**: Security and data isolation are critical for multi-user applications.

**Independent Test**: Can be tested by accessing the app without a token and verifying login prompt, then with a token verifying only user-owned tasks appear.

**Acceptance Scenarios**:

1. **Given** a user has no valid session/token, **When** they access the dashboard, **Then** they are prompted to log in
2. **Given** a user is authenticated, **When** they view their tasks, **Then** they only see tasks they created (not other users' tasks)

---

### Edge Cases

- What happens when the user's session expires while on the dashboard? Redirect to login with message
- How does the UI handle extremely long task titles? Truncate with ellipsis, show full on hover
- What happens when there are no tasks to display? Show empty state message encouraging task creation
- How does the system handle network errors during task creation? Show error toast with retry option

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a dark theme with background color #0F1115 and surface color #1A1D23
- **FR-002**: System MUST use teal (#2DD4BF) as primary accent color for active states and focus indicators
- **FR-003**: System MUST use amber (#FBBF24) for secondary accents, pending status badges, and primary action buttons
- **FR-004**: System MUST use green (#22C55E) for success states and completed task badges
- **FR-005**: System MUST display a top navigation bar with app name, navigation links (Dashboard, Tasks, AI Assistant), and user info
- **FR-006**: System MUST show a centered dashboard header with title "Manage Your Tasks" and subtitle
- **FR-007**: System MUST provide a task creation card with title (required) and description (optional) inputs
- **FR-008**: System MUST disable the Create Task button until the title field has valid input
- **FR-009**: System MUST show loading state on the Create Task button during form submission
- **FR-010**: System MUST display task status badges with amber for pending and green for completed
- **FR-011**: System MUST provide an AI Assistant card with "Open AI Assistant" CTA
- **FR-012**: System MUST implement hover effects and subtle transitions on interactive elements
- **FR-013**: System MUST display clear loading and error states for all async operations
- **FR-014**: System MUST show empty state messaging when no tasks exist
- **FR-015**: System MUST redirect unauthenticated users to login prompt
- **FR-016**: System MUST display only user-owned tasks (per-user isolation)
- **FR-017**: System MUST be responsive across mobile, tablet, and desktop viewports
- **FR-018**: System MUST use light gray tones for text to ensure readability on dark backgrounds

### Key Entities

- **Task**: User-created item with title, optional description, status (pending/completed), and owner reference
- **User**: Authenticated person with unique identity, owns multiple tasks
- **Navigation State**: Current active section (Dashboard, Tasks, AI Assistant)
- **Theme**: Dark color scheme configuration (background, surface, primary, secondary, success, text colors)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify the active navigation item within 1 second of viewing
- **SC-002**: Users can distinguish between pending and completed tasks instantly through color-coded badges
- **SC-003**: Users can create a new task in under 30 seconds from dashboard load
- **SC-004**: UI renders correctly across 320px (mobile), 768px (tablet), 1024px (laptop), and 1920px (desktop) viewports
- **SC-005**: All interactive elements have visible hover/focus states with teal accent
- **SC-006**: Text maintains a minimum contrast ratio of 4.5:1 against dark backgrounds for readability
- **SC-007**: Page loads and becomes interactive within 2 seconds on standard connections
- **SC-008**: 100% of users see only their own tasks (no data leakage between users)

## Scope

### In Scope
- Dark theme implementation with specified color palette
- Top navigation with active state indicators
- Dashboard header with title and subtitle
- Task creation card with form validation and loading states
- Task status display with color-coded badges
- AI Assistant card placeholder with CTA
- Responsive design for all major viewport sizes
- User authentication awareness (login prompt, user info display)

### Out of Scope
- Team collaboration features
- Analytics dashboard
- Admin UI
- Theme switching/customization (only dark theme)
- AI Assistant actual implementation (card UI only)

## Assumptions

- Existing backend API endpoints for task CRUD operations remain unchanged
- Session-based authentication continues to be used
- Users access the application via modern browsers (Chrome, Firefox, Safari, Edge)
- The existing task data model (title, description, completed, owner_id) is sufficient
