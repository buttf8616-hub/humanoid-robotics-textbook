# Research: Frontend Chat Integration

**Feature**: 004-frontend-chat-integration
**Date**: 2026-01-27

## Technical Context Resolution

### 1. Docusaurus Custom Component Pattern

**Decision**: Use `src/theme/Root.js` wrapper pattern to inject chat component globally

**Rationale**:
- Root component wraps the entire React tree, making chat accessible from all pages
- Persists state across navigations without re-mounting
- Standard Docusaurus pattern - no hacks required
- Does not require swizzling individual theme components

**Alternatives Considered**:
- Swizzle Layout component: More complex, higher maintenance burden
- Custom plugin: Overkill for a single component injection
- MDX component per page: Not scalable, requires manual addition to every page

**Implementation**:
```jsx
// src/theme/Root.js
import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
```

### 2. Environment Variable Configuration

**Decision**: Use `customFields` in `docusaurus.config.js` with dotenv for API URL configuration

**Rationale**:
- Standard Docusaurus pattern for passing env vars to client-side code
- Works with both local development (localhost) and production deployments
- No additional dependencies required beyond dotenv (already common)

**Alternatives Considered**:
- Hardcoded URLs: Not flexible for different environments
- Runtime fetch of config: Adds latency and complexity
- Build-time replacement: Less flexible, requires rebuild for URL changes

**Implementation**:
```javascript
// docusaurus.config.js
require('dotenv').config();

module.exports = {
  customFields: {
    chatApiUrl: process.env.CHAT_API_URL || 'http://localhost:8000',
  },
};
```

```javascript
// Component usage
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
const { siteConfig: { customFields } } = useDocusaurusContext();
const apiUrl = customFields.chatApiUrl;
```

### 3. State Management Approach

**Decision**: React useState/useReducer with Context API for chat state

**Rationale**:
- Conversation state is simple (messages array, loading, error)
- No need for external state management libraries
- Context API provides state persistence across page navigations
- Minimal bundle size impact

**Alternatives Considered**:
- Redux: Overkill for single-feature state
- Zustand: Additional dependency not justified
- Local component state only: Would lose state on navigation

**Implementation**:
```jsx
// ChatContext pattern
const ChatContext = React.createContext();

function ChatProvider({ children }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <ChatContext.Provider value={{ messages, isLoading, error, ... }}>
      {children}
    </ChatContext.Provider>
  );
}
```

### 4. API Communication

**Decision**: Use native fetch API with async/await

**Rationale**:
- axios is already in package.json but fetch is sufficient
- Reduces bundle size if we don't need axios interceptors
- Native browser API - no additional dependency
- Easy error handling with try/catch

**Alternatives Considered**:
- axios: Already installed, but overkill for single endpoint
- SWR/React Query: Adds caching complexity not needed for chat
- WebSocket: Backend uses REST, no real-time requirement

**Implementation**:
```javascript
async function sendMessage(question, conversationHistory, selectedContext) {
  const response = await fetch(`${apiUrl}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      conversation_history: conversationHistory,
      selected_context: selectedContext,
      top_k: 5,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }

  return response.json();
}
```

### 5. Text Selection Feature

**Decision**: Use Selection API with popover tooltip on selection

**Rationale**:
- Native browser API, no dependencies
- Common UX pattern (Medium, Notion)
- Can detect selection position for tooltip placement
- Works across all browsers

**Alternatives Considered**:
- Custom selection highlighting: Complex, may conflict with code blocks
- Right-click context menu only: Less discoverable
- Floating action button: Always visible, clutters UI

**Implementation**:
```javascript
// Listen for selection changes
document.addEventListener('selectionchange', handleSelection);

function handleSelection() {
  const selection = window.getSelection();
  if (selection.toString().trim().length > 0) {
    // Show "Ask about this" tooltip near selection
    showSelectionTooltip(selection);
  }
}
```

### 6. Markdown Rendering in Chat

**Decision**: Use react-markdown for rendering AI responses

**Rationale**:
- AI responses include markdown formatting (code blocks, lists, bold)
- Lightweight library, well-maintained
- Supports code syntax highlighting with plugins
- Works well with React

**Alternatives Considered**:
- dangerouslySetInnerHTML: Security risk with user-influenced content
- Custom regex parsing: Error-prone, incomplete markdown support
- MDX runtime: Overkill, adds significant bundle size

**New Dependency**: `react-markdown` (+ optional `remark-gfm` for tables)

### 7. Mobile Responsive Approach

**Decision**: CSS-based responsive design with slide-up drawer on mobile

**Rationale**:
- CSS media queries are performant and well-supported
- Slide-up drawer is familiar mobile UX pattern
- No JavaScript-based breakpoint detection needed
- Integrates with Docusaurus's existing responsive design

**Breakpoints**:
- Desktop (>996px): Fixed position sidebar chat panel
- Tablet (768-996px): Collapsible sidebar
- Mobile (<768px): Full-screen slide-up drawer

### 8. Accessibility Requirements

**Decision**: Follow WAI-ARIA guidelines for chat widgets

**Implementation Checklist**:
- `role="dialog"` for chat panel
- `aria-label` for input field
- Keyboard navigation (Escape to close, Tab through elements)
- Focus trap when chat is open on mobile
- Screen reader announcements for new messages
- Sufficient color contrast in both light/dark themes

### 9. Error Handling Strategy

**Decision**: User-friendly error messages with retry capability

**Error Types**:
| Error | User Message | Action |
|-------|-------------|--------|
| Network error | "Unable to connect. Check your internet connection." | Retry button |
| Backend 503 | "Service temporarily unavailable. Please try again." | Auto-retry after 5s |
| Backend 400 | "Please enter a valid question." | Clear input, focus |
| Backend timeout | "Taking too long. Please try again." | Retry button |
| Unknown error | "Something went wrong. Please try again." | Retry button |

### 10. Testing Strategy

**Decision**: Component testing with React Testing Library, E2E with Cypress

**Test Coverage**:
- Unit tests: State management, API calls, utility functions
- Component tests: Chat panel rendering, user interactions
- Integration tests: Full chat flow with mocked API
- E2E tests: Real browser interaction with running backend

## Dependencies Summary

### New Dependencies Required
```json
{
  "react-markdown": "^9.0.0",
  "remark-gfm": "^4.0.0"
}
```

### Existing Dependencies Used
- react, react-dom (already installed)
- clsx (already installed)
- @docusaurus/useDocusaurusContext (Docusaurus built-in)

### Dev Dependencies
```json
{
  "@testing-library/react": "^14.0.0",
  "@testing-library/jest-dom": "^6.0.0",
  "cypress": "^13.0.0"
}
```

## CORS Configuration Required

Backend must allow requests from frontend domain:

```python
# backend/src/main.py - Add to existing CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local dev
        "https://your-production-domain.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## File Structure Decision

```text
src/
├── components/
│   └── ChatWidget/
│       ├── index.js           # Main component
│       ├── ChatWidget.module.css
│       ├── ChatPanel.js       # Chat panel UI
│       ├── ChatMessage.js     # Single message component
│       ├── ChatInput.js       # Input field + send button
│       ├── SourceCitation.js  # Clickable source links
│       └── SelectionTooltip.js # "Ask about this" popup
├── context/
│   └── ChatContext.js         # State management
├── hooks/
│   └── useChatApi.js          # API communication hook
└── theme/
    └── Root.js                # Global wrapper injection
```

## Open Questions Resolved

1. **How to inject chat on all pages?** → Root.js wrapper
2. **How to configure API URL?** → customFields in docusaurus.config.js
3. **State management library?** → React Context (no external library)
4. **How to render markdown?** → react-markdown library
5. **Mobile UX pattern?** → Slide-up drawer
6. **Text selection approach?** → Native Selection API + tooltip
