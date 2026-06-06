# Implementation Plan: Frontend Chat Integration

**Branch**: `004-frontend-chat-integration` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-chat-integration/spec.md`

## Summary

Integrate a chat widget into the Docusaurus textbook frontend that communicates with the FastAPI RAG backend (Spec 003) to provide interactive Q&A. Users can ask questions about the book content, get AI-generated answers with source citations, ask about selected text, and maintain multi-turn conversations.

## Technical Context

**Language/Version**: JavaScript/JSX (ES2020+), Node.js LTS (for build)
**Primary Dependencies**: React 18.x, Docusaurus 3.x, react-markdown 9.x
**Storage**: N/A (session memory only - React Context)
**Testing**: Jest + React Testing Library (unit/component), Cypress (E2E)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web application (frontend extension to existing Docusaurus site)
**Performance Goals**: Chat response perceived latency < 3s UI, API response < 8s (95th percentile)
**Constraints**: Must work offline-gracefully (show error), mobile-responsive (320px+), accessible (WCAG 2.1 AA)
**Scale/Scope**: Single chat widget, ~10 React components, ~15 files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-First Development | PASS | Spec 004 created before implementation plan |
| II. AI-Assisted, Human-Directed | PASS | Plan follows user input, spec defines acceptance criteria |
| III. Source-Grounded Content | PASS | Chat widget consumes RAG API which grounds answers in book content |
| IV. Modular & Maintainable Documentation | PASS | Components follow Docusaurus patterns (src/theme, src/components) |
| V. Reproducibility & Transparency | PASS | Environment variables documented, build process standard |
| VI. Test-First (NON-NEGOTIABLE) | PENDING | Tests must be written before implementation |

**Post-Design Re-check**: All gates PASS. Test-First will be enforced in tasks.md.

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-chat-integration/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions
├── quickstart.md        # Usage guide
├── contracts/
│   └── chat-api.yaml    # OpenAPI contract
└── tasks.md             # Implementation tasks (from /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── components/
│   └── ChatWidget/
│       ├── index.js               # Main component export
│       ├── ChatWidget.js          # Widget container (toggle + panel)
│       ├── ChatWidget.module.css  # Widget styles
│       ├── ChatPanel.js           # Panel UI (header, messages, input)
│       ├── ChatPanel.module.css   # Panel styles
│       ├── ChatMessage.js         # Single message (user/assistant)
│       ├── ChatMessage.module.css # Message styles
│       ├── ChatInput.js           # Input field + send button
│       ├── ChatInput.module.css   # Input styles
│       ├── SourceCitation.js      # Clickable source link
│       ├── SourceCitation.module.css
│       ├── SelectionTooltip.js    # "Ask about this" popup
│       └── SelectionTooltip.module.css
├── context/
│   └── ChatContext.js             # State management (useReducer + Context)
├── hooks/
│   ├── useChatApi.js              # API communication hook
│   ├── useTextSelection.js        # Text selection detection
│   └── useKeyboardShortcuts.js    # Keyboard navigation
├── utils/
│   └── chatHelpers.js             # Utility functions
├── theme/
│   └── Root.js                    # Global wrapper (injects ChatWidget)
└── css/
    └── custom.css                 # Updated with chat CSS variables

tests/
├── unit/
│   ├── ChatContext.test.js
│   ├── useChatApi.test.js
│   └── chatHelpers.test.js
├── component/
│   ├── ChatWidget.test.js
│   ├── ChatPanel.test.js
│   ├── ChatMessage.test.js
│   └── ChatInput.test.js
└── e2e/
    └── chat-flow.cy.js            # Cypress E2E tests
```

**Structure Decision**: Single frontend extension to existing Docusaurus site. Components organized by feature (ChatWidget/), shared code in hooks/, context/, utils/. Theme extension via src/theme/Root.js.

## Implementation Phases

### Phase 1: Foundation (P1 - Core Chat)

**Goal**: Basic chat widget that opens/closes and displays static messages

**Components**:
1. ChatWidget (container with toggle button)
2. ChatPanel (panel UI shell)
3. ChatMessage (message display)
4. ChatInput (text input + send button)
5. ChatContext (state management)

**Deliverables**:
- [ ] Chat toggle button visible on all pages
- [ ] Panel opens/closes on click
- [ ] Messages render with user/assistant styling
- [ ] Input field captures text
- [ ] Basic keyboard navigation (Escape to close)

### Phase 2: API Integration (P1 - Core Chat)

**Goal**: Connect to backend and send/receive real messages

**Components**:
1. useChatApi hook
2. API error handling
3. Loading states

**Deliverables**:
- [ ] Questions sent to POST /api/v1/chat
- [ ] Responses displayed with markdown rendering
- [ ] Loading indicator while waiting
- [ ] Error messages displayed gracefully
- [ ] Environment variable configuration

### Phase 3: Source Citations (P1 - Core Chat)

**Goal**: Display and navigate to source references

**Components**:
1. SourceCitation component
2. Citation click handling

**Deliverables**:
- [ ] Sources displayed below answers
- [ ] Citation links navigate to book pages
- [ ] Confidence indicator shown

### Phase 4: Text Selection (P2)

**Goal**: Enable asking about selected text

**Components**:
1. SelectionTooltip
2. useTextSelection hook
3. Selected context passing

**Deliverables**:
- [ ] Tooltip appears on text selection
- [ ] "Ask about this" opens chat with context
- [ ] Backend receives URL/section filters
- [ ] Answers scoped to selection

### Phase 5: Conversation History (P3)

**Goal**: Multi-turn conversation support

**Components**:
1. History tracking in ChatContext
2. Conversation serialization

**Deliverables**:
- [ ] Previous messages sent with new questions
- [ ] Pronouns resolved correctly (follow-up questions)
- [ ] History persists across page navigation
- [ ] History clears on tab close

### Phase 6: Polish & Accessibility (P3)

**Goal**: Mobile support and accessibility

**Components**:
1. Mobile drawer UI
2. Keyboard shortcuts
3. ARIA labels
4. Theme integration

**Deliverables**:
- [ ] Mobile-responsive layout (slide-up drawer)
- [ ] Dark/light theme support
- [ ] Keyboard shortcuts (Ctrl+/, Tab navigation)
- [ ] Screen reader announcements
- [ ] Focus management

## Dependencies

### External Services
- **Backend RAG API** (Spec 003): POST /api/v1/chat - REQUIRED
- CORS must be configured on backend for frontend domain

### New npm Dependencies
```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "cypress": "^13.0.0"
  }
}
```

### Existing Dependencies Used
- react, react-dom (18.x)
- clsx (styling)
- @docusaurus/useDocusaurusContext (config access)

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| CHAT_API_URL | Backend API base URL | http://localhost:8000 | Yes |

### docusaurus.config.js Changes

```javascript
require('dotenv').config();

module.exports = {
  // ... existing config
  customFields: {
    chatApiUrl: process.env.CHAT_API_URL || 'http://localhost:8000',
  },
};
```

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend unavailable | Chat unusable | Graceful error message, retry button |
| Slow API responses | Poor UX | Loading indicator, 30s timeout, cancel option |
| CORS misconfiguration | No API access | Document CORS setup, test in dev |
| Bundle size increase | Slower page load | Code splitting, lazy load chat |
| Mobile keyboard issues | Input hidden | Viewport management, position: fixed |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat available on all doc pages | 100% | Automated test |
| Response time (UI perceived) | < 3s | Lighthouse, manual testing |
| Mobile usability | Full functionality | Manual testing on devices |
| Accessibility compliance | WCAG 2.1 AA | axe DevTools audit |
| Test coverage | > 80% | Jest coverage report |

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Follow TDD: Write tests first for each component
3. Implement Phase 1-6 incrementally
4. Run E2E tests before marking complete

## Artifacts Generated

- [x] research.md - Technical decisions and patterns
- [x] data-model.md - Entity definitions and types
- [x] contracts/chat-api.yaml - OpenAPI specification
- [x] quickstart.md - User guide
- [x] plan.md - This implementation plan
- [ ] tasks.md - To be generated via `/sp.tasks`
