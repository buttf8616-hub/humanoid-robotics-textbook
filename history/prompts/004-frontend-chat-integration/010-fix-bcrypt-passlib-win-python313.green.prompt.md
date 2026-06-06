---
id: 010
title: Fix bcrypt passlib incompatibility Windows Python 3.13
stage: green
date: 2026-06-07
surface: agent
model: claude-sonnet-4-6
feature: 004-frontend-chat-integration
branch: 004-frontend-chat-integration
user: fbutt042600@gmail.com
command: (session resume)
labels: ["bugfix","auth","bcrypt","passlib","backend","windows"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/auth_service.py
tests:
  - manual: POST /api/v1/auth/signin returns 200 with token
  - manual: POST /api/v1/content/personalize returns AI-adapted content
  - manual: POST /api/v1/content/translate returns Urdu translation
---

## Prompt

(Session resumed from previous context — backend signin returning 500 Internal Server Error on Windows Python 3.13. Need to debug and fix.)

## Response snapshot

Diagnosed root cause: `passlib[bcrypt]` is incompatible with `bcrypt` 5.0.0 installed on Windows Python 3.13. passlib tries to access `bcrypt.__about__.__version__` which no longer exists in bcrypt 4.x/5.x, causing `AttributeError` then `ValueError: password cannot be longer than 72 bytes`.

Fix: removed `passlib.context.CryptContext` from `auth_service.py` and replaced with direct `bcrypt` calls:
- `hash_password` → `bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()`
- `verify_password` → `bcrypt.checkpw(plain.encode(), hashed.encode())`

All endpoints now verified working:
- `POST /api/v1/auth/signin` → 200 with JWT token + user info
- `POST /api/v1/content/personalize` → Groq-powered AI-adapted content
- `POST /api/v1/content/translate` → Urdu translation with Nastaliq script

## Outcome

- ✅ Impact: Full auth flow restored — signin/signup/personalize/translate all working
- 🧪 Tests: All three API endpoints manually verified with HTTP requests
- 📁 Files: backend/src/services/auth_service.py (removed passlib dependency, use bcrypt directly)
- 🔁 Next prompts: Test full signup flow in browser UI; verify chapter actions buttons visible
- 🧠 Reflection: passlib is effectively unmaintained and breaks with bcrypt >= 4.0. Direct bcrypt usage is simpler and future-proof.

## Evaluation notes (flywheel)

- Failure modes observed: passlib incompatibility with modern bcrypt — silent 500 with no clear error in API response
- Graders run and results (PASS/FAIL): All manual API tests PASS
- Prompt variant (if applicable): null
- Next experiment: Add bcrypt version pin or remove passlib from pyproject.toml dependencies
