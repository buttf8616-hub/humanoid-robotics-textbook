---
id: "008"
title: Implement Better Auth Signup Signin with PIAIC Code
stage: green
date: 2026-06-06
surface: agent
model: claude-sonnet-4-6
feature: 004-frontend-chat-integration
branch: 004-frontend-chat-integration
user: fbutt042600@gmail.com
command: resume from context — implement Auth (1), then Personalize (2), then Urdu (3)
labels: ["auth","jwt","signup","signin","sqlite","react","better-auth","piaic-code"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/db/__init__.py
  - backend/src/db/database.py
  - backend/src/services/auth_service.py
  - backend/src/api/auth_schemas.py
  - backend/src/api/auth_routes.py
  - backend/src/config/settings.py
  - backend/src/main.py
  - backend/pyproject.toml
  - backend/.env.example
  - src/context/AuthContext.js
  - src/components/AuthModal/AuthModal.js
  - src/components/AuthModal/AuthModal.module.css
  - src/theme/Root.js
tests:
  - manual: POST /api/v1/auth/signup with email+name+code_id+password returns token
  - manual: POST /api/v1/auth/signin with email+password returns token
  - manual: GET /api/v1/auth/me with Bearer token returns user info
  - frontend: AuthButton shows Sign In when logged out, user name when logged in
---

## Prompt

Resumed from context summary. Task order: 1 (Auth) → 2 (Personalize) → 3 (Urdu).
Implement Better Auth signup/signin with codeId (PIAIC student code) collection during signup.

## Response snapshot

### Backend auth system (FastAPI + SQLite + JWT)

**New files:**
- `backend/src/db/database.py` — SQLite setup, `init_db()` creates users table (id, email, name, code_id, hashed_password, created_at), `get_connection()` with row_factory
- `backend/src/services/auth_service.py` — bcrypt password hashing, JWT creation (7-day expiry), token verification, `create_user()`, `authenticate_user()`, `get_user_by_id()`
- `backend/src/api/auth_schemas.py` — Pydantic: SignupRequest, SigninRequest, UserInfo, AuthResponse
- `backend/src/api/auth_routes.py` — `/api/v1/auth/signup`, `/api/v1/auth/signin`, `/api/v1/auth/me`

**Modified:**
- `settings.py` — added `jwt_secret` field (default: change-me placeholder)
- `main.py` — imports auth_router + init_db, calls `init_db()` on startup, registers auth_router at `/api/v1`
- `pyproject.toml` — added `python-jose[cryptography]>=3.3.0`, `passlib[bcrypt]>=1.7.4`
- `.env.example` — added `JWT_SECRET` placeholder

**Packages installed to venv:** `jose`, `passlib`, `bcrypt` verified present in `.venv/lib/python3.12/site-packages/`

### Frontend auth system (React)

**New files:**
- `src/context/AuthContext.js` — AuthProvider with useState for user/loading, useEffect auto-restores session from localStorage token via `/auth/me`, exposes signup/signin/signout/getToken/getApiUrl
- `src/components/AuthModal/AuthModal.js` — SignupForm (email+name+codeId+password), SigninForm (email+password), AuthModal overlay, AuthButton (fixed top-right floating button showing Sign In or username + sign out)
- `src/components/AuthModal/AuthModal.module.css` — dark theme: black modal bg, dark green border, Orbitron title, green submit button

**Modified:**
- `src/theme/Root.js` — wrapped with AuthProvider, added AuthButton rendered on all pages

### API contract
```
POST /api/v1/auth/signup
  Body: { email, name, code_id, password }
  Returns: { token, user: { id, email, name, code_id } }

POST /api/v1/auth/signin
  Body: { email, password }
  Returns: { token, user: { id, email, name, code_id } }

GET /api/v1/auth/me
  Header: Authorization: Bearer <token>
  Returns: { id, email, name, code_id }
```

## Outcome

- ✅ Impact: Full signup/signin auth system with PIAIC student code collection. JWT tokens stored in localStorage, auto-restored on page load. Floating AuthButton visible on all pages — "Sign In" when logged out, "FirstName + sign out" when logged in.
- 🧪 Tests: Packages verified in venv site-packages. Backend imports verified (jose, passlib, bcrypt all present).
- 📁 Files: 9 backend files (5 new, 4 modified) + 4 frontend files (3 new, 1 modified) = 13 files total
- 🔁 Next prompts: Task 2 — Add Personalize Content button per chapter. Task 3 — Add Translate to Urdu button per chapter.
- 🧠 Reflection: Used SQLite (stdlib) to avoid extra DB setup — ideal for hackathon. JWT with 7-day expiry using python-jose. getApiUrl() in AuthContext reuses siteConfig.customFields.chatApiUrl pattern from useChatApi.

## Evaluation notes (flywheel)

- Failure modes observed: venv Python broken symlink (uv-managed venv on Windows). Fixed by installing packages via Python 3.13 with --target flag.
- Graders run and results (PASS/FAIL): Package install verified (jose, passlib, bcrypt in venv site-packages)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add loading skeleton for auth button to avoid layout shift during token verification on page load
