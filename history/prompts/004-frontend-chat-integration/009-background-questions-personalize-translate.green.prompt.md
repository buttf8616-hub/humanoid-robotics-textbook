---
id: "009"
title: Background Questions Personalize Translate Urdu
stage: green
date: 2026-06-06
surface: agent
model: claude-sonnet-4-6
feature: 004-frontend-chat-integration
branch: 004-frontend-chat-integration
user: fbutt042600@gmail.com
command: implement 5 6 7 — background questions in signup, personalize button, translate to urdu button
labels: ["auth","background","personalization","urdu","translation","chapter-actions","docusaurus-swizzle"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/db/database.py
  - backend/src/services/auth_service.py
  - backend/src/services/content_service.py
  - backend/src/api/auth_schemas.py
  - backend/src/api/auth_routes.py
  - backend/src/api/content_routes.py
  - backend/src/main.py
  - src/context/AuthContext.js
  - src/components/AuthModal/AuthModal.js
  - src/components/AuthModal/AuthModal.module.css
  - src/components/ChapterActions/ChapterActions.js
  - src/components/ChapterActions/ChapterActions.module.css
  - src/theme/DocItem/Layout/index.js
tests:
  - signup step-2 collects software_background and hardware_background via radio cards
  - POST /api/v1/auth/signup stores background fields in SQLite
  - POST /api/v1/content/personalize returns personalized chapter for logged-in user
  - POST /api/v1/content/translate returns Urdu translation for logged-in user
  - ChapterActions bar appears on every doc page via DocItem/Layout swizzle
  - buttons open ResultModal with loading dots then rendered markdown
  - unauthenticated users see "Sign in" prompt instead of disabled buttons
---

## Prompt

User: "we have to work on 5 6 7"
- Point 5: Better Auth signup with background questions (software + hardware)
- Point 6: Personalize Content button at start of each chapter
- Point 7: Translate to Urdu button at start of each chapter

## Response snapshot

### Point 5 — Background questions in signup (2-step form)

**database.py**: Added `software_background` and `hardware_background` TEXT columns + migration via ALTER TABLE (silently ignores if columns already exist).

**auth_schemas.py**: SignupRequest gains `software_background` + `hardware_background` fields (optional, default ""). UserInfo includes both fields in response.

**auth_service.py**: `create_user()` updated to accept and store both background fields.

**auth_routes.py**: signup handler passes background fields; `_user_info()` helper maps all 6 UserInfo fields.

**AuthModal.js**: 2-step signup form:
- Step 1: Name, Email, PIAIC Code, Password (with step indicator bar)
- Step 2: Software background (Beginner/Intermediate/Advanced radio cards) + Hardware background (None/Basic/Intermediate/Advanced radio cards) + Back button
- Background questions explain they enable personalised content

### Point 6 — Personalize Content button

**content_service.py**: `ContentService.personalize()` — builds system prompt from user's stored background profile, calls Groq llama-3.3-70b-versatile. Adapts tone: beginner gets analogies and no code; advanced gets specs and code examples.

**content_routes.py**: `POST /api/v1/content/personalize` — requires Bearer token, reads user background from DB, calls ContentService, returns `{ result, user_name }`.

**ChapterActions.js**: Bar with "🎯 Personalize Content" button. Reads page content from `document.querySelector('article').innerText`. Opens ResultModal with loading dots → renders markdown result.

### Point 7 — Translate to Urdu button

**content_service.py**: `ContentService.translate_to_urdu()` — system prompt instructs Groq to translate to Nastaliq Urdu script, keep technical terms in English with parenthetical Urdu, preserve markdown structure.

**content_routes.py**: `POST /api/v1/content/translate` — same auth pattern, returns Urdu translation.

**ChapterActions.js**: "🌐 Translate to Urdu" button (blue) in same bar. Same ResultModal pattern.

### DocItem Layout swizzle

**src/theme/DocItem/Layout/index.js**: Wraps `@theme-original/DocItem/Layout` and prepends `<ChapterActions />` — the bar appears at the top of every documentation chapter page automatically.

### UX for unauthenticated users
- Buttons are visible (not disabled) but clicking opens SignIn/SignUp modal
- "Sign in to use AI features" hint with inline Sign in link shown on the right

## Outcome

- ✅ Impact: Full bonus feature set implemented — 2-step signup with background profile, AI-powered content personalisation per chapter, Urdu translation per chapter. All behind JWT auth.
- 🧪 Tests: Logic verified by code review. Backend content routes require valid JWT. Frontend reads DOM content for AI processing.
- 📁 Files: 13 files total (4 new: content_service, content_routes, ChapterActions, DocItem/Layout; 9 updated)
- 🔁 Next: Push to GitHub + redeploy on Vercel; user tests personalization and translation on a chapter
- 🧠 Reflection: Using DOM `.innerText` for content extraction is simpler than re-fetching Qdrant chunks and works for all pages regardless of ingestion status.

## Evaluation notes (flywheel)

- Failure modes: Groq max_tokens may need tuning for long chapters (currently capped at 6000 chars input)
- Graders: code review — imports, route registration, modal flow all verified
- Prompt variant: null
- Next experiment: Cache personalized content per user+URL to avoid re-calling Groq on every click
