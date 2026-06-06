# Quick Start: Frontend Chat Integration

This guide shows how to use the chat widget integrated into the Docusaurus textbook frontend.

## Prerequisites

1. Backend RAG service running (Spec 003)
2. Docusaurus frontend running locally or deployed
3. CORS configured on backend for frontend domain

## Local Development Setup

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### 2. Configure Frontend Environment

Create a `.env` file in the project root:

```bash
# .env
CHAT_API_URL=http://localhost:8000
```

### 3. Start the Frontend

```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

## Using the Chat Widget

### Opening the Chat

Click the chat icon button (floating in the bottom-right corner) to open the chat panel.

**Keyboard shortcut**: Press `Ctrl+/` (or `Cmd+/` on Mac) to toggle the chat panel.

### Asking Questions

1. Type your question in the input field
2. Press Enter or click the Send button
3. Wait for the AI response (loading indicator will show)
4. View the answer with source citations

**Example questions:**
- "What is embodied intelligence?"
- "How does ROS 2 handle inter-process communication?"
- "Explain the difference between sensors and actuators"

### Viewing Source Citations

Each answer includes source citations. Click on a citation link to navigate to the relevant section in the book.

**Citation format:**
```
[Source: Page Title - Section Name]
```

### Follow-up Questions

The chat maintains conversation context. You can ask follow-up questions using pronouns:

1. Ask: "What is ROS 2?"
2. Follow up: "What are its main features?"

The agent understands "its" refers to ROS 2.

### Asking About Selected Text

1. Highlight text in the book
2. Click "Ask about this" in the popup
3. Type your question about the selected content
4. The agent will answer based only on that section

**Example:**
- Select a paragraph about sensor fusion
- Ask: "Explain this in simpler terms"
- Get an answer scoped to that specific content

### Closing the Chat

- Click the X button in the panel header
- Click outside the panel (on mobile)
- Press Escape key

## Response Confidence Levels

| Level | Meaning |
|-------|---------|
| **High** | Answer is well-supported by multiple sources |
| **Medium** | Answer has moderate source support |
| **Low** | Limited source support, answer may be incomplete |
| **Refused** | No relevant content found; question may be off-topic |

## Error Handling

| Error Message | What to Do |
|--------------|------------|
| "Unable to connect" | Check your internet connection |
| "Service temporarily unavailable" | Wait a moment and retry |
| "Please enter a valid question" | Enter a non-empty question |
| "Taking too long" | Click retry; backend may be overloaded |

## Production Deployment

### Environment Configuration

Set the production API URL before building:

```bash
# For Vercel
vercel env add CHAT_API_URL production
# Value: https://your-backend-domain.com

# For Netlify
netlify env:set CHAT_API_URL https://your-backend-domain.com

# For manual builds
export CHAT_API_URL=https://your-backend-domain.com
npm run build
```

### CORS Configuration

Ensure your backend allows requests from the frontend domain:

```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local dev
        "https://your-frontend.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Build and Deploy

```bash
# Build the static site
npm run build

# Deploy to hosting platform
# (Vercel, Netlify, or your preferred host)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chat button not visible | Ensure JavaScript is enabled; check console for errors |
| "Network error" on submit | Verify backend is running and CORS is configured |
| No sources in response | Question may be off-topic; try rephrasing |
| Slow responses | Check backend logs; may be rate-limited by OpenRouter |
| Styling issues | Clear browser cache; check CSS is loaded |

## API Reference

The chat widget communicates with the backend via:

```
POST /api/v1/chat
```

See `contracts/chat-api.yaml` for full OpenAPI specification.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+/` (or `Cmd+/`) | Toggle chat panel |
| `Escape` | Close chat panel |
| `Enter` | Submit question |
| `Shift+Enter` | New line in input |
| `Tab` | Navigate between elements |
