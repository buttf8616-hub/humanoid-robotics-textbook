# Tasks: AI Agent with Retrieval-Augmented Answering

**Input**: Design documents from `/specs/003-ai-agent-rag/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Constitution specifies Test-First (TDD) approach. Tests are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (backend)**: `backend/src/`, `backend/tests/`
- Extending existing Spec 001/002 backend structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: OpenRouter SDK configuration and agent module structure

- [x] T001 Add openai dependency (openai>=1.55.0) to backend/pyproject.toml
- [x] T002 [P] Add OPENROUTER_API_KEY to backend/src/config/settings.py
- [x] T003 [P] Add OPENROUTER_API_KEY to backend/.env.example with documentation
- [x] T004 [P] Add agent configuration settings (model, temperature, max_tokens) to backend/src/config/settings.py
- [x] T005 Create backend/src/agent/ module with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create system prompt template in backend/src/agent/prompts.py with grounding enforcement rules
- [x] T007 [P] Create AgentMessage model in backend/src/models/agent.py
- [x] T008 [P] Create SelectedContext model in backend/src/models/agent.py
- [x] T009 [P] Create SourceCitation model in backend/src/models/agent.py
- [x] T010 Export agent models from backend/src/models/__init__.py
- [x] T011 Define retrieve_book_content tool function signature in backend/src/agent/tools.py
- [x] T012 Implement retrieve_book_content tool using @function_tool decorator in backend/src/agent/tools.py
- [x] T013 Add httpx call to POST /api/v1/search within retrieve_book_content tool in backend/src/agent/tools.py
- [x] T014 [P] Write unit test for retrieve_book_content tool in backend/tests/unit/test_agent_tools.py
- [x] T015 Create AgentService class skeleton in backend/src/agent/agent_service.py
- [x] T016 Initialize OpenAI Agent with system prompt and tools in AgentService.__init__ in backend/src/agent/agent_service.py
- [x] T017 Export AgentService from backend/src/agent/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Full-Book Context Answering (Priority: P1) 🎯 MVP

**Goal**: Agent retrieves relevant book chunks, generates grounded answers with citations, refuses when no content found

**Independent Test**: Send question "What is embodied intelligence?" to POST /api/v1/chat. Verify agent calls retrieval tool, returns answer grounded in chunks, includes source citations, refuses off-topic queries.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T018 [P] [US1] Write unit test for AgentService.answer() calls retrieval tool in backend/tests/unit/test_agent_service.py
- [x] T019 [P] [US1] Write unit test for AgentService.answer() includes citations in backend/tests/unit/test_agent_service.py
- [x] T020 [P] [US1] Write unit test for AgentService.answer() refuses when no results in backend/tests/unit/test_agent_service.py
- [x] T021 [P] [US1] Write integration test for POST /chat returns grounded answer in backend/tests/integration/test_chat_api.py
- [x] T022 [P] [US1] Write integration test for POST /chat refuses off-topic query in backend/tests/integration/test_chat_api.py

### Implementation for User Story 1

- [x] T023 [P] [US1] Create ChatRequest schema in backend/src/api/schemas.py (question, top_k fields)
- [x] T024 [P] [US1] Create ChatResponse schema in backend/src/api/schemas.py (answer, sources, confidence, latency_ms, tokens_used)
- [x] T025 [US1] Implement AgentService.answer() method in backend/src/agent/agent_service.py
- [x] T026 [US1] Use Runner.run() to invoke agent with user query in AgentService.answer()
- [x] T027 [US1] Parse agent response and extract generated answer in AgentService.answer()
- [x] T028 [US1] Parse tool call results to extract retrieval chunks in AgentService.answer()
- [x] T029 [US1] Format source citations from retrieved chunks in AgentService.answer()
- [x] T030 [US1] Implement confidence detection (high/medium/low/refused) based on response in AgentService.answer()
- [x] T031 [US1] Add latency measurement using time.perf_counter() in AgentService.answer()
- [x] T032 [US1] Add token usage tracking from OpenAI response in AgentService.answer()
- [x] T033 [US1] Add POST /api/v1/chat endpoint in backend/src/api/routes.py
- [x] T034 [US1] Instantiate AgentService and call answer() in POST /chat route handler
- [x] T035 [US1] Add input validation (empty query check) in POST /chat endpoint
- [x] T036 [US1] Add error handling for OpenAI API errors (return 503) in POST /chat endpoint
- [x] T037 [US1] Add error handling for retrieval service errors (return 503) in POST /chat endpoint
- [x] T038 [US1] Add structured logging for agent requests (query, results count, latency) in POST /chat endpoint

**Checkpoint**: User Story 1 complete - basic agent answering functional with citations and refusal logic

---

## Phase 4: User Story 2 - User-Selected Text Context (Priority: P2)

**Goal**: Agent applies URL/section filters for focused answering when user highlights specific text

**Independent Test**: Send question with selected_context (URL + section) to POST /api/v1/chat. Verify agent applies filters to retrieval, answers only from filtered chunks.

### Tests for User Story 2

- [x] T039 [P] [US2] Write unit test for retrieve_book_content passes url_filter to /search in backend/tests/unit/test_agent_tools.py
- [x] T040 [P] [US2] Write unit test for retrieve_book_content passes section_filter to /search in backend/tests/unit/test_agent_tools.py
- [x] T041 [P] [US2] Write integration test for POST /chat with selected_context filters results in backend/tests/integration/test_chat_api.py
- [x] T042 [P] [US2] Write integration test for POST /chat acknowledges insufficient filtered context in backend/tests/integration/test_chat_api.py

### Implementation for User Story 2

- [x] T043 [US2] Extend ChatRequest schema to include optional selected_context field in backend/src/api/schemas.py
- [x] T044 [US2] Modify retrieve_book_content tool to accept url_filter and section_filter parameters in backend/src/agent/tools.py
- [x] T045 [US2] Pass filters from tool parameters to httpx /search call in backend/src/agent/tools.py
- [x] T046 [US2] Update AgentService.answer() to extract selected_context from request in backend/src/agent/agent_service.py
- [x] T047 [US2] Modify agent instructions to acknowledge context boundaries when filters applied in backend/src/agent/prompts.py
- [x] T048 [US2] Pass selected_context to agent run context in AgentService.answer()
- [x] T049 [US2] Validate that response sources match filtered URL/section in AgentService.answer()

**Checkpoint**: User Story 2 complete - filtered retrieval working for user-selected text

---

## Phase 5: User Story 3 - Conversation Context Awareness (Priority: P3)

**Goal**: Agent maintains conversation history and resolves pronouns in follow-up questions

**Independent Test**: Send sequence of related questions to POST /api/v1/chat. Verify second question with pronoun ("What are its components?") correctly interprets referent from first question.

### Tests for User Story 3

- [x] T050 [P] [US3] Write unit test for conversation history formatting for OpenAI API in backend/tests/unit/test_agent_service.py
- [x] T051 [P] [US3] Write unit test for AgentService handles conversation history in backend/tests/unit/test_agent_service.py
- [x] T052 [P] [US3] Write integration test for multi-turn conversation maintains context in backend/tests/integration/test_chat_api.py
- [x] T053 [P] [US3] Write integration test for pronoun resolution in follow-up question in backend/tests/integration/test_chat_api.py

### Implementation for User Story 3

- [x] T054 [US3] Extend ChatRequest schema to include optional conversation_history field in backend/src/api/schemas.py
- [x] T055 [US3] Implement conversation history formatting method in AgentService in backend/src/agent/agent_service.py
- [x] T056 [US3] Convert Message objects to OpenAI message format (role, content) in backend/src/agent/agent_service.py
- [x] T057 [US3] Add conversation history to agent context in AgentService.answer()
- [x] T058 [US3] Update system prompt template to include conversation context section in backend/src/agent/prompts.py
- [x] T059 [US3] Implement token budget management (sliding window for long conversations) in backend/src/agent/agent_service.py
- [x] T060 [US3] Add conversation turn limit configuration (default 10 turns) to settings.py

**Checkpoint**: User Story 3 complete - multi-turn conversations working with pronoun resolution

---

## Phase 6: Grounding Validation & Quality Assurance

**Purpose**: Ensure zero-hallucination compliance and citation accuracy

- [x] T061 [P] Write grounding validation test (verify answer content matches retrieved chunks) in backend/tests/integration/test_agent_grounding.py
- [x] T062 [P] Write citation validation test (verify citations reference actual sources) in backend/tests/integration/test_agent_grounding.py
- [x] T063 [P] Write hallucination prevention test (verify refusal on empty results) in backend/tests/integration/test_agent_grounding.py
- [x] T064 [P] Write off-topic query test suite (10 queries outside book domain) in backend/tests/integration/test_agent_grounding.py
- [x] T065 Implement post-processing validation (check citations exist in chunks) in AgentService.answer()
- [x] T066 Add logging for refusal events (no results / off-topic queries) in AgentService.answer()

---

## Phase 7: Error Handling & Resilience

**Purpose**: Robust error handling for production readiness

- [x] T067 Implement exponential backoff for OpenAI API rate limits in AgentService
- [x] T068 [P] Add timeout configuration for OpenAI requests (default 4 seconds) in settings.py
- [x] T069 [P] Add timeout configuration for retrieval service calls (default 3 seconds) in backend/src/agent/tools.py
- [x] T070 Implement circuit breaker pattern for retrieval service in backend/src/agent/tools.py
- [x] T071 Add graceful degradation message for service failures in POST /chat endpoint
- [x] T072 [P] Write integration test for OpenAI API timeout handling in backend/tests/integration/test_chat_api.py
- [x] T073 [P] Write integration test for retrieval service timeout handling in backend/tests/integration/test_chat_api.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, deployment, and final validation

- [x] T074 [P] Update backend/README.md with POST /api/v1/chat endpoint documentation
- [x] T075 [P] Add usage examples with curl commands to backend/README.md
- [x] T076 [P] Create quickstart.md with agent interaction examples in specs/003-ai-agent-rag/
- [x] T077 [P] Add environment variable documentation for OPENAI_API_KEY
- [x] T078 Update backend/Dockerfile to include openai dependency (via pyproject.toml)
- [x] T079 Add health check endpoint for agent service in backend/src/api/routes.py
- [x] T080 Run full test suite (unit + integration + grounding) and verify all pass
- [x] T081 Perform manual validation against success criteria (SC-001 to SC-007)
- [x] T082 [P] Document monitoring metrics (token usage, latency, refusal rate) in specs/003-ai-agent-rag/
- [x] T083 [P] Add Hugging Face Spaces deployment instructions for OPENAI_API_KEY secret

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (P1): Core answering - MUST complete first
  - US2 (P2): Filtered context - can run after US1
  - US3 (P3): Conversation history - can run after US1
- **Grounding Validation (Phase 6)**: Can run in parallel with or after US1
- **Error Handling (Phase 7)**: Can run after US1
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (P1) | Foundational | None (must complete first) |
| US2 (P2) | US1 | US3, Phase 6, Phase 7 |
| US3 (P3) | US1 | US2, Phase 6, Phase 7 |

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/schemas before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004 can run in parallel (different settings)
```

**Phase 2 (Foundational)**:
```
T007, T008, T009 can run in parallel (different models)
T014 can run in parallel with T015-T017
```

**Phase 3 (US1)**:
```
T018, T019, T020, T021, T022 can run in parallel (tests)
T023, T024 can run in parallel (schemas)
```

**Phase 5 (US3)**:
```
T050, T051, T052, T053 can run in parallel (tests)
```

**Phase 6 (Grounding)**:
```
T061, T062, T063, T064 can run in parallel (tests)
```

**Phase 7 (Error Handling)**:
```
T068, T069 can run in parallel (config)
T072, T073 can run in parallel (tests)
```

**Phase 8 (Polish)**:
```
T074, T075, T076, T077, T082, T083 can run in parallel (documentation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T017)
3. Complete Phase 3: User Story 1 (T018-T038)
4. **STOP and VALIDATE**: Test basic agent answering independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Add Grounding + Error Handling → Validate → Deploy
6. Add Polish → Final deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T017)
2. Once Foundational is done:
   - Developer A: User Story 1 (T018-T038)
   - Developer B: Start on User Story 2 tests (T039-T042)
3. After US1 complete:
   - Developer A: User Story 2 implementation (T043-T049)
   - Developer B: User Story 3 (T050-T060)
   - Developer C: Grounding validation (T061-T066)
4. Final phases in parallel by different developers

---

## Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Setup | 5 | 2 |
| Foundational | 12 | 5 |
| US1 (P1) | 21 | 7 |
| US2 (P2) | 11 | 4 |
| US3 (P3) | 11 | 4 |
| Grounding | 6 | 4 |
| Error Handling | 7 | 4 |
| Polish | 10 | 6 |
| **Total** | **83** | **36** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- OpenAI Agents SDK documentation referenced via Context7 MCP for tool definitions
