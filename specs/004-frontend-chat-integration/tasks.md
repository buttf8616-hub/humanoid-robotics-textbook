# Tasks: Frontend Chat Integration

**Input**: Design documents from `/specs/004-frontend-chat-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## User Story Mapping

| Story | Priority | Title | Description |
|-------|----------|-------|-------------|
| US1 | P1 | Ask Questions About Book Content | Core chat functionality with API integration |
| US2 | P2 | Ask Questions About Selected Text | Text selection with scoped answering |
| US3 | P3 | Multi-Turn Conversation | Conversation history support |
| US4 | P3 | Mobile-Friendly Chat Experience | Mobile responsive design |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and configuration

- [x] T001 Install new dependencies: react-markdown, remark-gfm in package.json
- [x] T002 Create .env file with CHAT_API_URL=http://localhost:8000
- [x] T003 Update docusaurus.config.js to add customFields.chatApiUrl from environment
- [x] T004 [P] Create src/components/ChatWidget/ directory structure
- [x] T005 [P] Create src/context/ directory for state management
- [x] T006 [P] Create src/hooks/ directory for custom hooks
- [x] T007 [P] Create src/utils/ directory for helper functions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create ChatContext with useReducer in src/context/ChatContext.js
- [x] T009 Implement initial state: messages[], inputValue, isOpen, isLoading, error, selectedContext
- [x] T010 Implement reducer actions: OPEN_PANEL, CLOSE_PANEL, TOGGLE_PANEL, SET_INPUT, SET_LOADING, SET_ERROR, CLEAR_ERROR
- [x] T011 Create ChatProvider component that wraps children with ChatContext.Provider
- [x] T012 Create useChatContext hook for consuming context
- [x] T013 Create src/theme/Root.js to wrap entire app with ChatProvider
- [x] T014 [P] Create chatHelpers.js with generateMessageId() utility in src/utils/chatHelpers.js
- [x] T015 [P] Create CSS variables for chat theming in src/css/custom.css (light/dark mode)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Ask Questions About Book Content (Priority: P1) MVP

**Goal**: Users can open a chat panel, type questions, submit to backend API, and see answers with source citations

**Independent Test**: Open the book website, click the chat button, type "What is embodied intelligence?", submit, and verify an answer appears with source citations that link back to relevant book sections.

### Implementation for User Story 1

#### 3.1 Chat Widget Container

- [x] T016 [P] [US1] Create ChatWidget.js component shell in src/components/ChatWidget/ChatWidget.js
- [x] T017 [P] [US1] Create ChatWidget.module.css with toggle button styles in src/components/ChatWidget/ChatWidget.module.css
- [x] T018 [US1] Implement toggle button that shows/hides chat panel using ChatContext
- [x] T019 [US1] Position toggle button fixed bottom-right corner (desktop)
- [x] T020 [US1] Create index.js export in src/components/ChatWidget/index.js

#### 3.2 Chat Panel UI

- [x] T021 [P] [US1] Create ChatPanel.js component shell in src/components/ChatWidget/ChatPanel.js
- [x] T022 [P] [US1] Create ChatPanel.module.css with panel layout in src/components/ChatWidget/ChatPanel.module.css
- [x] T023 [US1] Implement panel header with title and close button
- [x] T024 [US1] Implement messages container with scroll behavior
- [x] T025 [US1] Implement panel positioning (fixed sidebar on desktop)
- [x] T026 [US1] Handle Escape key to close panel

#### 3.3 Chat Input

- [x] T027 [P] [US1] Create ChatInput.js component in src/components/ChatWidget/ChatInput.js
- [x] T028 [P] [US1] Create ChatInput.module.css with input styling in src/components/ChatWidget/ChatInput.module.css
- [x] T029 [US1] Implement text input field with placeholder
- [x] T030 [US1] Implement Send button with icon
- [x] T031 [US1] Handle Enter key submission
- [x] T032 [US1] Prevent empty/whitespace-only submissions (FR-011)
- [x] T033 [US1] Disable input and button during loading state

#### 3.4 API Integration

- [x] T034 [US1] Create useChatApi.js hook in src/hooks/useChatApi.js
- [x] T035 [US1] Implement getApiUrl() to read from useDocusaurusContext customFields
- [x] T036 [US1] Implement sendMessage(question) function with fetch POST to /api/v1/chat
- [x] T037 [US1] Add request timeout handling (30 seconds)
- [x] T038 [US1] Parse ChatResponse and map to ChatMessage format
- [x] T039 [US1] Add ADD_USER_MESSAGE and ADD_ASSISTANT_MESSAGE reducer actions in ChatContext
- [x] T040 [US1] Wire useChatApi to ChatInput submission flow
- [x] T041 [US1] Display loading indicator while awaiting response (FR-004)

#### 3.5 Message Display

- [x] T042 [P] [US1] Create ChatMessage.js component in src/components/ChatWidget/ChatMessage.js
- [x] T043 [P] [US1] Create ChatMessage.module.css with message bubble styling in src/components/ChatWidget/ChatMessage.module.css
- [x] T044 [US1] Implement user message styling (right-aligned, primary color)
- [x] T045 [US1] Implement assistant message styling (left-aligned, secondary color)
- [x] T046 [US1] Integrate react-markdown for rendering assistant message content (FR-005)
- [x] T047 [US1] Configure remark-gfm plugin for tables and strikethrough
- [x] T048 [US1] Display message timestamp

#### 3.6 Source Citations

- [x] T049 [P] [US1] Create SourceCitation.js component in src/components/ChatWidget/SourceCitation.js
- [x] T050 [P] [US1] Create SourceCitation.module.css in src/components/ChatWidget/SourceCitation.module.css
- [x] T051 [US1] Render citation as clickable link with title and section
- [x] T052 [US1] Display relevance score as visual indicator (badge)
- [x] T053 [US1] Implement click handler to navigate to book section (FR-006)
- [x] T054 [US1] Display confidence level indicator below answer

#### 3.7 Error Handling

- [x] T055 [US1] Implement error state display in ChatPanel (FR-010)
- [x] T056 [US1] Show user-friendly error messages per error type (network, 503, 400, timeout)
- [x] T057 [US1] Add retry button for recoverable errors
- [x] T058 [US1] Handle backend 503 with auto-retry after 5 seconds

#### 3.8 Integration

- [x] T059 [US1] Update Root.js to import and render ChatWidget component
- [x] T060 [US1] Verify chat toggle visible on all doc pages
- [x] T061 [US1] Test full flow: open panel → type question → submit → see answer with citations

**Checkpoint**: User Story 1 complete - basic chat Q&A with source citations working

---

## Phase 4: User Story 2 - Ask Questions About Selected Text (Priority: P2)

**Goal**: Users can select text in the book, click "Ask about this", and get answers scoped to that selection

**Independent Test**: On a book page, highlight a paragraph about ROS 2, click "Ask about selection", type "Explain this in simpler terms", and verify the answer references only the selected content.

### Implementation for User Story 2

#### 4.1 Text Selection Hook

- [x] T062 [P] [US2] Create useTextSelection.js hook in src/hooks/useTextSelection.js
- [x] T063 [US2] Implement selection change listener using Selection API
- [x] T064 [US2] Extract selected text, position (top, left), and bounding rect
- [x] T065 [US2] Detect current page URL using window.location
- [x] T066 [US2] Detect nearest section header from selection parent elements
- [x] T067 [US2] Filter out code block selections (optional: allow or block)

#### 4.2 Selection Tooltip

- [x] T068 [P] [US2] Create SelectionTooltip.js component in src/components/ChatWidget/SelectionTooltip.js
- [x] T069 [P] [US2] Create SelectionTooltip.module.css in src/components/ChatWidget/SelectionTooltip.module.css
- [x] T070 [US2] Render tooltip positioned near selection
- [x] T071 [US2] Display "Ask about this" button in tooltip
- [x] T072 [US2] Handle tooltip positioning near viewport edges
- [x] T073 [US2] Hide tooltip when selection cleared

#### 4.3 Context Integration

- [x] T074 [US2] Add SET_SELECTED_CONTEXT action to ChatContext reducer
- [x] T075 [US2] Wire tooltip click to set selectedContext in state
- [x] T076 [US2] Auto-open chat panel when "Ask about this" clicked
- [x] T077 [US2] Display selected context preview in ChatPanel header area
- [x] T078 [US2] Add "Clear context" button to remove selection filter

#### 4.4 API Integration for Selected Context

- [x] T079 [US2] Update useChatApi.sendMessage to accept selectedContext parameter
- [x] T080 [US2] Include selected_context (url, section) in API request body
- [x] T081 [US2] Pass selectedContext from ChatContext to useChatApi
- [x] T082 [US2] Clear selectedContext after successful question submission (or keep for follow-ups)

#### 4.5 Validation

- [x] T083 [US2] Test selection on regular paragraph text
- [x] T084 [US2] Test selection spanning multiple paragraphs
- [x] T085 [US2] Verify backend receives URL and section filters correctly

**Checkpoint**: User Story 2 complete - text selection with scoped answering working

---

## Phase 5: User Story 3 - Multi-Turn Conversation (Priority: P3)

**Goal**: Users can have multi-turn conversations with context preserved across questions

**Independent Test**: Ask "What is ROS 2?", wait for response, then ask "What are its main features?" and verify the second answer understands "its" refers to ROS 2.

### Implementation for User Story 3

#### 5.1 Conversation History Management

- [x] T086 [US3] Update ChatContext to track conversation history as array
- [x] T087 [US3] Implement history serialization: convert ChatMessage[] to ConversationHistoryItem[]
- [x] T088 [US3] Limit history to last 6 messages (3 turns) per research.md maxHistoryLength
- [x] T089 [US3] Preserve history across page navigations (Context persists in Root.js)

#### 5.2 API Integration for History

- [x] T090 [US3] Update useChatApi.sendMessage to accept conversationHistory parameter
- [x] T091 [US3] Include conversation_history array in API request body
- [x] T092 [US3] Pass serialized history from ChatContext to useChatApi

#### 5.3 UI Enhancements

- [x] T093 [US3] Ensure messages container scrolls to show new messages
- [x] T094 [US3] Allow scrolling up to view previous messages
- [x] T095 [US3] Add CLEAR_CONVERSATION action to reset history
- [x] T096 [US3] Add "New conversation" button to clear history and start fresh

#### 5.4 Validation

- [x] T097 [US3] Test pronoun resolution ("What is X?" → "What are its features?")
- [x] T098 [US3] Test navigation between pages preserves history
- [x] T099 [US3] Verify history clears on browser tab close (no persistence)

**Checkpoint**: User Story 3 complete - multi-turn conversations working

---

## Phase 6: User Story 4 - Mobile-Friendly Chat Experience (Priority: P3)

**Goal**: Chat interface works well on mobile devices with appropriate UX patterns

**Independent Test**: Open the book on a mobile device (or emulator at 375px width), open the chat panel, submit a question, and verify the interface is usable and answers are readable.

### Implementation for User Story 4

#### 6.1 Mobile Layout

- [x] T100 [P] [US4] Add CSS media queries for mobile breakpoint (<768px) in ChatWidget.module.css
- [x] T101 [P] [US4] Add mobile styles to ChatPanel.module.css for full-screen drawer
- [x] T102 [US4] Implement slide-up drawer animation for mobile panel
- [x] T103 [US4] Position toggle button appropriately for mobile (bottom-right, larger tap target)

#### 6.2 Mobile Input Handling

- [x] T104 [US4] Ensure input field stays visible when mobile keyboard opens
- [x] T105 [US4] Add viewport meta handling for keyboard appearance
- [x] T106 [US4] Test touch interactions (tap to open, swipe to close optional)

#### 6.3 Mobile UX Polish

- [x] T107 [US4] Ensure text is readable without horizontal scrolling
- [x] T108 [US4] Add close button in mobile drawer header (tap outside to close)
- [x] T109 [US4] Test on various mobile screen widths (320px, 375px, 414px)

**Checkpoint**: User Story 4 complete - mobile chat experience working

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, theme integration, and final polish

### Accessibility (WCAG 2.1 AA)

- [x] T110 [P] Add role="dialog" and aria-label to ChatPanel
- [x] T111 [P] Add aria-label to input field and buttons
- [x] T112 Implement focus trap when chat panel is open (especially mobile)
- [x] T113 Add screen reader announcements for new messages (aria-live region)
- [x] T114 Ensure Tab navigation works through all interactive elements
- [x] T115 Add keyboard shortcut Ctrl+/ (Cmd+/ on Mac) to toggle chat panel

### Theme Integration

- [x] T116 [P] Implement dark mode styles using Docusaurus CSS variables
- [x] T117 Test light/dark mode toggle with chat open
- [x] T118 Verify sufficient color contrast in both themes

### Keyboard Shortcuts

- [x] T119 Create useKeyboardShortcuts.js hook in src/hooks/useKeyboardShortcuts.js
- [x] T120 Implement Ctrl+/ toggle shortcut
- [x] T121 Document keyboard shortcuts in UI (tooltip or help text)

### Final Validation

- [x] T122 Run full E2E test: all user stories working together
- [x] T123 Verify chat available on 100% of doc pages (SC-002)
- [x] T124 Test CORS configuration with backend
- [x] T125 Update quickstart.md if any steps changed
- [x] T126 Run accessibility audit (axe DevTools or similar)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS all user stories)
    ↓
    ├── Phase 3: User Story 1 (P1) - MVP
    │       ↓
    ├── Phase 4: User Story 2 (P2) - can start after US1 or in parallel
    │       ↓
    ├── Phase 5: User Story 3 (P3) - can start after US1 or in parallel
    │       ↓
    └── Phase 6: User Story 4 (P3) - can start after US1 or in parallel
            ↓
        Phase 7: Polish (after all desired stories complete)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (P1) | Phase 2 only | - |
| US2 (P2) | Phase 2 only | US1, US3, US4 |
| US3 (P3) | Phase 2 only | US1, US2, US4 |
| US4 (P3) | Phase 2 only | US1, US2, US3 |

**Note**: While user stories can technically run in parallel after Phase 2, sequential P1→P2→P3 order is recommended for single developer to ensure MVP (US1) is complete first.

### Within Each User Story

1. Component shells (marked [P]) can be created in parallel
2. CSS files (marked [P]) can be created in parallel with components
3. Logic implementation follows component structure
4. Integration and validation tasks come last

---

## Parallel Execution Examples

### Phase 1 Parallel Tasks

```bash
# These can all run simultaneously:
T004: Create src/components/ChatWidget/ directory
T005: Create src/context/ directory
T006: Create src/hooks/ directory
T007: Create src/utils/ directory
```

### Phase 3 (US1) Parallel Tasks

```bash
# Component shells can be created in parallel:
T016: Create ChatWidget.js shell
T021: Create ChatPanel.js shell
T027: Create ChatInput.js shell
T042: Create ChatMessage.js shell
T049: Create SourceCitation.js shell

# CSS files can be created in parallel:
T017: ChatWidget.module.css
T022: ChatPanel.module.css
T028: ChatInput.module.css
T043: ChatMessage.module.css
T050: SourceCitation.module.css
```

### Cross-Story Parallel (with multiple developers)

```bash
# Developer A: User Story 1 (T016-T061)
# Developer B: User Story 2 (T062-T085) - after Phase 2
# Developer C: User Story 3 (T086-T099) - after Phase 2
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015)
3. Complete Phase 3: User Story 1 (T016-T061)
4. **STOP and VALIDATE**: Test chat Q&A independently
5. Deploy/demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → Deploy (MVP!)
3. Add User Story 2 → Test → Deploy (Text Selection)
4. Add User Story 3 → Test → Deploy (Conversations)
5. Add User Story 4 → Test → Deploy (Mobile)
6. Polish phase → Final release

---

## Task Summary

| Phase | Tasks | Task IDs |
|-------|-------|----------|
| Phase 1: Setup | 7 | T001-T007 |
| Phase 2: Foundational | 8 | T008-T015 |
| Phase 3: US1 (MVP) | 46 | T016-T061 |
| Phase 4: US2 | 24 | T062-T085 |
| Phase 5: US3 | 14 | T086-T099 |
| Phase 6: US4 | 10 | T100-T109 |
| Phase 7: Polish | 17 | T110-T126 |
| **Total** | **126** | T001-T126 |

### Tasks per User Story

| User Story | Task Count | Priority |
|------------|------------|----------|
| US1: Ask Questions | 46 | P1 (MVP) |
| US2: Selected Text | 24 | P2 |
| US3: Multi-Turn | 14 | P3 |
| US4: Mobile | 10 | P3 |

### Parallel Opportunities

- **Phase 1**: 4 directory creation tasks (T004-T007)
- **Phase 2**: 2 utility tasks (T014-T015)
- **Phase 3**: 10 component/CSS shell tasks
- **Phase 4**: 4 component/CSS shell tasks
- **Phase 6**: 2 CSS tasks
- **Phase 7**: 3 accessibility tasks, 2 theme tasks

---

## Notes

- Constitution mandates TDD but tests not explicitly requested - focus on implementation
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend (Spec 003) must be running for full integration testing
