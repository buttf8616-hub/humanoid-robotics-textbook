---
id: 0002
title: AI Agent RAG Implementation Plan
stage: plan
date: 2026-01-22
surface: agent
model: claude-sonnet-4-5
feature: 003-ai-agent-rag
branch: 003-ai-agent-rag
user: fahad
command: /sp.plan
labels: ["planning", "ai-agent", "rag", "openai-sdk", "architecture"]
links:
  spec: specs/003-ai-agent-rag/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/003-ai-agent-rag/plan.md
tests:
 - N/A (planning phase)
---

## Prompt

/sp.plan
- Initialize OpenAI Agents SDK within FastAPI backend
- Define retrieval tool interface connected to Spec-2 endpoint
- Implement agent logic to enforce retrieval-first answering
- Add support for selected-text–only question answering
- Expose agent interaction endpoint for frontend use

## Response snapshot

Created comprehensive implementation plan for AI Agent with Retrieval-Augmented Answering:

**Architecture**:
- Agent orchestration layer using OpenAI Agents SDK + GPT-4
- Custom tool function `retrieve_book_content` calling internal /search endpoint
- System prompt enforcing zero-hallucination policy with citation requirements
- New `backend/src/agent/` module for agent logic (AgentService, tools, prompts)
- New POST /api/v1/chat endpoint for frontend integration

**Implementation Phases**:
1. **Phase 2.1 - Foundation**: Setup OpenAI SDK, AgentService class, tool definitions, system prompts
2. **Phase 2.2 - US1 Full-Book Context (P1/MVP)**: Agent answers with retrieval, citations, refusal logic
3. **Phase 2.3 - US2 User-Selected Text (P2)**: URL/section filtering for focused context
4. **Phase 2.4 - US3 Conversation Context (P3)**: Multi-turn dialogue with history maintenance
5. **Phase 2.5 - Polish**: Documentation, testing, validation, deployment

**Key Contracts**:
- **Tool Interface**: `retrieve_book_content(query, top_k, url_filter, section_filter)` → retrieval results
- **API Endpoint**: `POST /api/v1/chat` with ChatRequest (question, history, context) → ChatResponse (answer, sources, confidence)
- **System Prompt**: Enforces ALWAYS call retrieval, ONLY use retrieved content, ALWAYS cite sources, refuse if no content

**Data Models**:
- AgentRequest, AgentResponse, Message, SourceCitation, SelectedContext
- Conversation history as list of Message objects
- Confidence levels: high, medium, low, refused

**Testing Strategy**:
- TDD: Unit tests for AgentService, tool functions BEFORE implementation
- Integration tests for /chat endpoint with grounding validation
- Automated checks: 100% retrieval invocation, 95% citation rate, zero hallucination
- Manual validation: Pronoun resolution (80%), content grounding audit (90%)

**Risk Mitigation**:
- Rate limits: Exponential backoff, token monitoring
- Hallucination: Strong system prompt, post-processing validation
- Latency: Streaming (if available), 4-second timeout, <500ms retrieval
- Token budget: Sliding window history, chunk truncation

**Dependencies**:
- OpenAI API (GPT-4 + Agents SDK) - new external dependency
- Spec 002 /search endpoint - existing internal dependency
- Spec 001 populated Qdrant - existing transitive dependency

## Outcome

- ✅ Impact: Complete architectural design for agent orchestration layer with retrieval-augmented generation
- 🧪 Tests: Testing strategy defined with TDD approach, unit + integration + grounding tests, success criteria validation plan
- 📁 Files: plan.md (490+ lines) with technical context, architecture, phases, contracts, risks
- 🔁 Next prompts: Phase 0 research.md (OpenAI SDK patterns), Phase 1 contracts/data-model/quickstart, /sp.tasks for detailed breakdown
- 🧠 Reflection: Architecture extends existing backend cleanly with isolated agent/ module. Core challenge is enforcing zero-hallucination through system prompt design and validation. Tool-calling pattern ensures agent always retrieves before answering.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan aligns with spec requirements and existing architecture
- Graders run and results (PASS/FAIL): Constitution check PASS (TDD enforced, spec-first, no violations)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Phase 0 research - prototype OpenAI tool calling pattern to validate enforcement mechanism
