---
id: "007"
title: Switch to Groq LLM and Apply Snow White Charcoal Dark Green Theme
stage: green
date: 2026-06-06
surface: agent
model: claude-sonnet-4-6
feature: 004-frontend-chat-integration
branch: 004-frontend-chat-integration
user: fbutt042600@gmail.com
command: continue (resumed from context summary)
labels: ["groq","theme","css","chat-widget","llm-switch","docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/.env
  - backend/src/config/settings.py
  - backend/src/agent/agent_service.py
  - backend/src/api/routes.py
  - src/css/custom.css
  - docusaurus.config.js
  - src/components/ChatWidget/ChatPanel.module.css
tests:
  - manual curl POST /chat verified working with Groq llama-3.3-70b-versatile
---

## Prompt

Resumed from context summary. Tasks pending:
1. Gemini 2.5-flash daily quota exhausted → switch backend to Groq
2. Change Docusaurus book theme — went through multiple iterations (orange, navy/cyan, black/gold, blue/slate, carbon/teal, snow white+bright green, snow white+red, slate+coral)
3. Final request: re-apply Option 2 (Snow White & Charcoal) but with DARKER green accent + fix AI chat widget going off-screen

## Response snapshot

### Groq integration
- Added GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS to backend/.env
- Added Groq config fields to settings.py
- Switched AgentService.__init__ from Gemini to AsyncOpenAI(base_url=groq_base_url)
- Fixed hardcoded "gemini" in routes.py 503 error handler → "groq"
- Verified working: llama-3.3-70b-versatile returns proper RAG answers with tool calls

### Chat widget off-screen fix
- Changed ChatPanel.module.css .chatPanel from position: absolute to position: fixed
- Added max-height: calc(100vh - 100px) to prevent overflow on small screens
- Mobile: full-screen overlay (top:0 left:0 right:0 bottom:0) with slide-up animation

### Snow White & Charcoal with darker green theme
- Primary color changed from bright #22c55e → dark forest #15803d
- Light variant #16a34a, lighter #22c55e (only for accents)
- White (#ffffff) page background, charcoal (#18181b) navbar/footer/code blocks
- H3 bullet dot, code gradient bar, active sidebar link, blockquote border all use #15803d
- Dark mode: green shifts to #22c55e as primary (readable on dark bg)
- Code theme: github (light) + dracula (dark) replacing vsDark/vsDark

## Outcome

- ✅ Impact: Backend now uses Groq free tier (14,400 req/day) — no more quota exhaustion. Frontend theme is Snow White & Charcoal with dark forest green accent as requested.
- 🧪 Tests: Manual chat API test via curl confirmed Groq llama-3.3-70b-versatile responds correctly with tool calls and RAG citations.
- 📁 Files: 7 files modified across backend config/services and frontend CSS/config
- 🔁 Next prompts: User review of final theme; potential dark mode fine-tuning; production deployment
- 🧠 Reflection: Iterative theme feedback required 8+ rounds. User's final preference was clean white base + charcoal headers + dark forest green for credibility/tech feel. Chat widget off-screen was a CSS specificity issue (absolute inside fixed = no viewport constraint).

## Evaluation notes (flywheel)

- Failure modes observed: AskUserQuestion tool max 4 options (rejected 5-option ask); PowerShell 60s timeout on slow Groq cold-start; Gemini quota exhaustion mid-session
- Graders run and results (PASS/FAIL): manual /chat endpoint PASS with Groq
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add a loading skeleton to chat widget while Groq warms up (cold start ~15-20s)
