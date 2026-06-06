# Data Model: Frontend Chat Integration

**Feature**: 004-frontend-chat-integration
**Date**: 2026-01-27

## Entities

### ChatMessage

Represents a single message in the conversation (user or assistant).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique message identifier (UUID) |
| role | 'user' \| 'assistant' | Yes | Who sent the message |
| content | string | Yes | Message text content |
| timestamp | Date | Yes | When message was created |
| sources | SourceCitation[] | No | Source citations (assistant only) |
| confidence | 'high' \| 'medium' \| 'low' \| 'refused' | No | Confidence level (assistant only) |
| isLoading | boolean | No | True while awaiting response |
| error | string | No | Error message if request failed |

**Validation Rules**:
- `content` must be non-empty for user messages
- `sources` only present when `role === 'assistant'`
- `id` must be unique within conversation

### SourceCitation

Represents a source reference from the AI response.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| url | string | Yes | Full URL to source page |
| title | string | Yes | Page title |
| section | string | Yes | Section header |
| chunkIndex | number | Yes | Position in page (0-based) |
| score | number | Yes | Relevance score (0.0-1.0) |
| excerpt | string | Yes | First ~100 characters of content |

**Validation Rules**:
- `url` must be a valid URL
- `score` must be between 0.0 and 1.0
- `excerpt` should not exceed 150 characters

### ConversationState

Represents the entire chat state managed by React Context.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| messages | ChatMessage[] | Yes | [] | All messages in conversation |
| inputValue | string | Yes | '' | Current input field value |
| isOpen | boolean | Yes | false | Whether chat panel is open |
| isLoading | boolean | Yes | false | Whether awaiting API response |
| error | string \| null | Yes | null | Current error message |
| selectedContext | SelectedContext \| null | Yes | null | User-selected text context |

**State Transitions**:

```
Initial → Panel Open (user clicks toggle)
Panel Open → Loading (user submits question)
Loading → Message Added (API success)
Loading → Error (API failure)
Error → Loading (user retries)
Panel Open → Closed (user clicks toggle or Escape)
Any → Selected Context Set (user selects text)
```

### SelectedContext

Represents user-selected text for focused answering.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| url | string | Yes | Current page URL |
| section | string \| null | No | Detected section header |
| text | string | Yes | Selected text content |
| position | { top, left } | No | Position for tooltip placement |

**Validation Rules**:
- `text` must be non-empty (whitespace trimmed)
- `url` must be current page URL

### ChatConfiguration

Application configuration (from environment/build).

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| apiUrl | string | Yes | 'http://localhost:8000' | Backend API base URL |
| maxHistoryLength | number | No | 10 | Max conversation turns to send |
| defaultTopK | number | No | 5 | Default number of chunks to retrieve |
| requestTimeout | number | No | 30000 | API request timeout (ms) |

## Type Definitions (TypeScript)

```typescript
// types/chat.ts

export type MessageRole = 'user' | 'assistant';
export type Confidence = 'high' | 'medium' | 'low' | 'refused';

export interface SourceCitation {
  url: string;
  title: string;
  section: string;
  chunkIndex: number;
  score: number;
  excerpt: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  sources?: SourceCitation[];
  confidence?: Confidence;
  isLoading?: boolean;
  error?: string;
}

export interface SelectedContext {
  url: string;
  section: string | null;
  text: string;
  position?: { top: number; left: number };
}

export interface ConversationState {
  messages: ChatMessage[];
  inputValue: string;
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  selectedContext: SelectedContext | null;
}

export interface ChatConfiguration {
  apiUrl: string;
  maxHistoryLength?: number;
  defaultTopK?: number;
  requestTimeout?: number;
}

// API Types (matching backend schema)
export interface ConversationHistoryItem {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  question: string;
  top_k?: number;
  selected_context?: {
    url: string;
    section?: string;
  };
  conversation_history?: ConversationHistoryItem[];
}

export interface TokenUsage {
  prompt: number;
  completion: number;
  total: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  confidence: Confidence;
  latency_ms: number;
  tokens_used: TokenUsage;
}
```

## State Management Actions

```typescript
// context/ChatContext.ts

type ChatAction =
  | { type: 'OPEN_PANEL' }
  | { type: 'CLOSE_PANEL' }
  | { type: 'TOGGLE_PANEL' }
  | { type: 'SET_INPUT'; payload: string }
  | { type: 'SUBMIT_QUESTION' }
  | { type: 'ADD_USER_MESSAGE'; payload: ChatMessage }
  | { type: 'ADD_ASSISTANT_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_SELECTED_CONTEXT'; payload: SelectedContext | null }
  | { type: 'CLEAR_CONVERSATION' };
```

## Relationships

```
ConversationState
    ├── messages[] ─────────► ChatMessage
    │                              └── sources[] ─► SourceCitation
    └── selectedContext ────► SelectedContext
```

## Session Storage

Conversation state is **not persisted** across browser sessions per spec requirements:
- State is managed in React Context (memory only)
- Closing browser tab clears all conversation history
- No localStorage/sessionStorage usage for messages

## Data Flow

```
User Input → ChatContext.dispatch(SET_INPUT)
           → ChatContext.dispatch(SUBMIT_QUESTION)
           → useChatApi.sendMessage()
           → Backend POST /api/v1/chat
           → ChatContext.dispatch(ADD_ASSISTANT_MESSAGE)
           → UI renders new message
```
