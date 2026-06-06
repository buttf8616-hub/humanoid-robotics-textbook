---
id: "006"
title: Verify End-to-End System Running
stage: green
date: 2026-06-06
surface: agent
model: claude-sonnet-4-6
feature: 004-frontend-chat-integration
branch: 004-frontend-chat-integration
user: fbutt042600@gmail.com
command: continue (context resumed)
labels: ["verification","frontend","backend","rag","chat","gemini","docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - (read-only verification — no file changes)
tests:
  - GET http://localhost:8000/health → 200 healthy
  - GET http://localhost:3000 → Docusaurus HTML (Physical AI & Humanoid Robotics)
  - GET http://localhost:8000/api/v1/verify → 353 vectors, 16 URLs, status ready
  - POST http://localhost:8000/api/v1/search query="humanoid robot definition" → 5 results, score 0.66
  - POST http://localhost:8000/api/v1/chat question="What is sensor fusion?" → full cited answer, confidence low
  - Two-turn Gemini agent flow tested manually → tool call + answer generation both working
---

## Prompt

(Continued from prior context) User reported http://localhost:8000 shows nothing. Frontend (Docusaurus) was not started. Need to start it and verify both servers running.

## Response snapshot

Confirmed both services are running:
- Backend FastAPI on localhost:8000 — healthy, 353 vectors, Gemini 2.5-flash responding
- Frontend Docusaurus on localhost:3000 — textbook site loading, chat widget wired to localhost:8000

Sensor fusion test query returned detailed answer with 6 citations from Chapter 2 and Chapter 3. The chatApiUrl in docusaurus.config.js defaults to http://localhost:8000 so no config change needed.

## Outcome

- ✅ Impact: Full RAG system verified end-to-end — frontend chat widget calls backend which retrieves from Qdrant and generates answers via Gemini 2.5-flash
- 🧪 Tests: health check, verify endpoint, search, chat all passing
- 📁 Files: no changes — verification pass only
- 🔁 Next prompts: user can open localhost:3000 to use the textbook chat; consider deploying backend to production URL so Vercel-hosted frontend can use it
- 🧠 Reflection: The confusion was port 8000 = API (no HTML), port 3000 = Docusaurus frontend. Both must run simultaneously for the chat to work.

## Evaluation notes (flywheel)

- Failure modes observed: Gemini 2.5-flash returns "I don't have information" for generic questions ("what is a humanoid robot?") when retrieved chunks don't contain a direct definition — this is correct grounded behavior, not a bug
- Graders run and results (PASS/FAIL): manual API tests PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): test with question phrasing that matches textbook content more precisely; or enrich system prompt to be less strict about "irrelevant results"
