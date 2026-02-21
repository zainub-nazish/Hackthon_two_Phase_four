# Tasks: Todo AI Chatbot (013-todo-ai-chatbot)

**Input**: Design documents from `/specs/013-todo-ai-chatbot/`
**Branch**: `013-todo-ai-chatbot` | **Date**: 2026-02-21
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅ | quickstart.md ✅

**Format**: `- [ ] [ID] [P?] [Story?] Description with file path`
- **[P]** = parallelizable (different files, no blocking dependencies)
- **[USn]** = maps to User Story n from spec.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project directories, dependencies, environment configuration

- [x] T001 Create backend directory structure: `backend/{auth,models,routes,services,tests}/` per plan.md
- [x] T002 [P] Create `backend/requirements.txt` with: fastapi, uvicorn, sqlmodel, asyncpg, openai-agents, mcp, pydantic-settings, python-jose[cryptography], aiosqlite, pytest, pytest-asyncio, httpx
- [x] T003 [P] Create `backend/.env.example` with: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `OPENAI_API_KEY`, `BETTER_AUTH_URL`, `DEBUG`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create `backend/config.py` — `pydantic-settings` `Settings` class reading `DATABASE_URL`, `BETTER_AUTH_SECRET`, `OPENAI_API_KEY`, `DEBUG`; export `settings` singleton
- [x] T005 [P] Create `backend/database.py` — async engine (`asyncpg+postgresql`), `SQLModel.metadata.create_all()` at startup, `get_session()` async generator, `get_async_session_maker()` for tool use
- [x] T006 [P] Create `backend/models/database.py` — SQLModel `table=True` classes: `Task` (id UUID PK, owner_id str indexed, title str max 200, description str nullable max 2000, completed bool default False, created_at/updated_at datetime), `Conversation` (id UUID PK, owner_id str indexed, created_at/updated_at datetime), `Message` (id UUID PK, conversation_id UUID FK→conversations.id indexed, role str max 20, content str, created_at datetime), `ToolCall` (id UUID PK, message_id UUID FK→messages.id indexed, tool_name str max 100, parameters str, result str, status str max 20, created_at datetime)
- [x] T007 [P] Create `backend/models/schemas.py` — Pydantic models: `ChatRequest` (message str, conversation_id UUID nullable), `ChatResponse` (conversation_id UUID, response str, tool_calls list[ToolCallResponse]), `ToolCallResponse` (tool_name, parameters, result, status), `MessageResponse` (id, conversation_id, role, content, created_at), `MessagesResponse` (conversation_id, messages list), `ConversationResponse` (conversation_id nullable, created_at nullable, updated_at nullable), `CurrentUser` (id str, email str)
- [x] T008 Create `backend/auth/dependencies.py` — `verify_user_owns_resource` FastAPI dependency: extracts Bearer JWT, verifies `BETTER_AUTH_SECRET`, checks `user_id` path param equals JWT `sub` claim, returns `CurrentUser`; raises 401/403 on failure
- [x] T009 [P] Create `backend/services/mcp_tools.py` — `FastMCP("todo-tools")` server instance, `_get_db_session()` async context manager (uses `get_async_session_maker()`), stdio entry point (`if __name__ == "__main__": server.run(transport="stdio")`); leave tool handler stubs (filled in Phase 3–7)
- [x] T010 [P] Create `backend/services/ai_agent.py` — `AIAgentService` class with `SYSTEM_PROMPT` (identity + tool-use instruction + `user_id` injection), `generate_response(messages, user_id) -> AgentResponse`; `AgentResponse` dataclass (`content: str`, `tool_calls: list[ToolCallRecord]`); `get_ai_agent_service()` dependency factory; leave agentic loop implementation for Phase 3
- [x] T011 Create `backend/tests/conftest.py` — pytest fixtures: `test_app` (FastAPI test client with DB and auth override), `db_session` (aiosqlite in-memory async session), `mcp_db` (in-memory session for MCP tool tests), `override_auth` (CurrentUser stub bypassing JWT)
- [x] T012 Create `backend/main.py` — FastAPI app, CORS middleware (allow `*` in dev), include chat router, lifespan context that calls `create_db_and_tables()`, `/health` GET returning `{"status": "ok", "db": bool, "ai": bool}`

**Checkpoint**: App starts (`uvicorn backend.main:app --reload --port 8000`), `/health` returns 200, `/docs` shows routes

---

## Phase 3: User Story 1 — Create a Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: User types "Add buy groceries to my list" → AI calls `add_task` → task created → confirmation returned

**Independent Test**: `POST /api/v1/users/{id}/chat` with `{"message": "Add buy milk"}` returns `response` containing confirmation and `tool_calls[0].tool_name == "add_task"`

### Implementation

- [x] T013 [US1] Implement `add_task` handler in `backend/services/mcp_tools.py` — strip/validate title (max 200), validate description (max 2000), insert `Task` via DB session, return `{id: str(uuid), title, description, completed}` on success or `{is_error: true, error: str}` on failure
- [x] T014 [US1] Implement `generate_response()` in `backend/services/ai_agent.py` — create `Agent` with `MCPServerStdio(command="python", args=["backend/services/mcp_tools.py"], cache_tools_list=True)`, inject `user_id` into system prompt, call `Runner.run(agent, messages)`, extract final text content and tool call records into `AgentResponse`
- [x] T015 [US1] Create `backend/routes/chat.py` — `APIRouter(prefix="/api/v1/users/{user_id}")`, `POST /chat` endpoint: strip/validate message, create or verify `Conversation`, persist `Message(role="user")`, load last 20 messages as context (`MAX_CONTEXT_MESSAGES = 20`), call `agent.generate_response()`, persist `Message(role="assistant")` + `ToolCall` records, update `conversation.updated_at`, return `ChatResponse`
- [x] T016 [US1] Register chat router in `backend/main.py` — `app.include_router(chat_router)`
- [x] T017 [US1] Write unit tests for `add_task` in `backend/tests/test_mcp_tools.py` — test: success creates task, empty title returns `is_error`, title > 200 chars returns `is_error`, description > 2000 chars returns `is_error`, task appears in DB after creation
- [x] T018 [US1] Write integration test for create intent in `backend/tests/test_chat.py` — test: `POST /chat` with stub agent returns 200 with `conversation_id` + `response`, new conversation created when `conversation_id` null, empty message returns 400, whitespace-only message returns 400

**Checkpoint**: US1 fully functional — type "Add buy groceries" in chat, task appears in task list

---

## Phase 4: User Story 2 — View Task List (Priority: P2)

**Goal**: User types "Show my tasks" → AI calls `list_tasks` → formatted list returned

**Independent Test**: Create 3 tasks then `POST /chat` with "Show pending tasks" → response lists only pending tasks; `list_tasks` tool called with `status="pending"`

### Implementation

- [x] T019 [US2] Implement `list_tasks` handler in `backend/services/mcp_tools.py` — query `Task` where `owner_id == user_id`, apply status filter (`pending` → `completed==False`, `completed` → `completed==True`, `all` → no filter), order by `created_at DESC`, return `{tasks: [{id, title, description, completed}], count: int}` or `{is_error: true, error: str}`
- [x] T020 [US2] Write unit tests for `list_tasks` in `backend/tests/test_mcp_tools.py` — test: returns empty list when no tasks, returns all tasks with `status=all`, `status=pending` excludes completed, `status=completed` excludes pending, count matches tasks length, user isolation (user B cannot see user A's tasks)

**Checkpoint**: US2 functional — "Show my tasks" returns formatted list; "Show pending tasks" filters correctly

---

## Phase 5: User Story 3 — Complete a Task (Priority: P3)

**Goal**: User types "Mark buy groceries as done" → AI calls `list_tasks` to find UUID → calls `complete_task` → task marked completed

**Independent Test**: Create task, `POST /chat` "Mark it done" → `complete_task` tool called → `list_tasks` shows task as completed

### Implementation

- [x] T021 [US3] Implement `complete_task` handler in `backend/services/mcp_tools.py` — validate `task_id` is valid UUID string, query `Task` where `id == task_uuid AND owner_id == user_id`, set `completed = True` + `updated_at = utcnow()`, commit, return `{id, title, completed: true}` or `{is_error: true, error: str}` (not found, invalid UUID)
- [x] T022 [US3] Write unit tests for `complete_task` in `backend/tests/test_mcp_tools.py` — test: success sets completed=True, invalid UUID returns `is_error`, task_not_found returns `is_error`, wrong user returns `is_error` (user isolation)

**Checkpoint**: US3 functional — tasks can be marked complete; completed tasks show in filtered list

---

## Phase 6: User Story 4 — Delete a Task (Priority: P4)

**Goal**: User types "Remove the groceries task" → AI calls `list_tasks` to find UUID → calls `delete_task` → task permanently removed

**Independent Test**: Create task, `POST /chat` "Delete it" → `delete_task` called → `list_tasks` shows empty list

### Implementation

- [x] T023 [US4] Implement `delete_task` handler in `backend/services/mcp_tools.py` — validate `task_id` UUID, query task with user isolation, `await session.delete(task)`, commit, return `{success: true, deleted_task_id: str}` or `{is_error: true, error: str}`
- [x] T024 [US4] Write unit tests for `delete_task` in `backend/tests/test_mcp_tools.py` — test: success removes task from DB (verify via list_tasks), task_not_found returns `is_error`, wrong user returns `is_error`, invalid UUID returns `is_error`

**Checkpoint**: US4 functional — tasks permanently deleted; they no longer appear in list

---

## Phase 7: User Story 5 — Update a Task (Priority: P5)

**Goal**: User types "Rename gym task to Morning workout" → AI calls `list_tasks` → calls `update_task` → title updated

**Independent Test**: Create task "Go to gym", `POST /chat` "Rename it to Morning workout" → `update_task` called → task title changed

### Implementation

- [x] T025 [US5] Implement `update_task` handler in `backend/services/mcp_tools.py` — validate `task_id` UUID, require at least one of `title`/`description`, strip and validate title (max 200), validate description (max 2000), update fields, set `updated_at = utcnow()`, return `{id, title, description, completed}` or `{is_error: true, error: str}`
- [x] T026 [US5] Write unit tests for `update_task` in `backend/tests/test_mcp_tools.py` — test: title update only, description update only, both fields update, neither field provided returns `is_error`, empty title returns `is_error`, task_not_found returns `is_error`, wrong user returns `is_error`

**Checkpoint**: US5 functional — all 5 CRUD operations available via natural language chat

---

## Phase 8: Conversation History & Persistence (FR-006)

**Purpose**: Multi-turn conversation — context loads on each request, history restores on page reload

**Goal**: User's conversation persists across page refreshes; AI remembers last 10 exchanges

**Independent Test**: Send 3 messages in sequence; `GET /conversations/{id}/messages` returns all 3 user + 3 assistant messages in chronological order

### Implementation

- [x] T027 Implement `GET /conversations` endpoint in `backend/routes/chat.py` — query `Conversation` where `owner_id == user_id` order by `updated_at DESC LIMIT 1`, return `ConversationResponse` (null `conversation_id` if none found)
- [x] T028 [P] Implement `GET /conversations/{conversation_id}/messages` endpoint in `backend/routes/chat.py` — verify conversation ownership, query `Message` where `conversation_id == id` order by `created_at ASC`, return `MessagesResponse`
- [x] T029 Write integration tests for history endpoints in `backend/tests/test_chat.py` — test: `GET /conversations` returns null when no conversations, returns most recent after chat, `GET /messages` returns ordered messages, 404 on wrong conversation_id, 403 on other user's conversation

---

## Phase 9: Frontend Integration (ChatKit UI)

**Purpose**: Connect ChatKit UI to `/api/{user_id}/chat` with Bearer auth and conversation state

**Goal**: User logs in → navigates to `/chat` → types message → AI responds — all via ChatKit component

**Independent Test**: Open browser at `/chat`, send "Add buy milk", verify task appears in sidebar task list

### Implementation

- [x] T030 Create `frontend/src/app/(dashboard)/chat/page.tsx` — ChatKit page component with auth guard; calls `GET /api/v1/users/{id}/conversations` on mount to load `conversation_id`; calls `GET /api/v1/users/{id}/conversations/{id}/messages` to restore history; renders ChatKit `<Chat>` component
- [x] T031 [P] Implement chat API calls in `frontend/src/lib/chat-api.ts` — `sendMessage(userId, message, conversationId?)` → `POST /api/v1/users/{userId}/chat`, `getRecentConversation(userId)`, `getMessages(userId, conversationId)` — all using `apiClient()` (auto-attaches Bearer)
- [x] T032 [P] Configure `frontend/vercel.json` rewrites — proxy `/api/*` to HF Space backend URL so ChatKit calls appear same-origin
- [x] T033 Configure `frontend/src/app/(dashboard)/chat/page.tsx` — manage `conversationId` state; pass it in subsequent `sendMessage` calls; update state when new `conversation_id` returned from first message

**Checkpoint**: Full end-to-end — user can create, list, complete, delete, update tasks via chat UI; conversation persists across refresh

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, isolation tests, operational readiness

- [x] T034 [P] Write user isolation tests in `backend/tests/test_chat_isolation.py` — test: user A cannot read user B's conversations or messages (403/404), user B cannot access user A's tasks via chat (AI responds "not found")
- [x] T035 [P] Write AI agent stub tests in `backend/tests/test_ai_agent.py` — test: `generate_response()` returns `AgentResponse` with `content` and `tool_calls`; stub agent bypasses real OpenAI call; tool dispatch returns correct structure
- [x] T036 [P] Verify all MCP tool `is_error` edge cases in `backend/tests/test_mcp_tools.py` — test: each tool handles DB unavailable gracefully, returns `is_error` not exception
- [x] T037 Add `backend/tests/test_chat_isolation.py` cross-user ToolCall test — verify that `ToolCall` records are only accessible to the conversation owner
- [x] T038 Run quickstart.md E2E validation — start server, run all cURL examples from quickstart.md, confirm each returns expected shape; document any deviations
- [x] T039 Verify HF Space deployment — set `OPENAI_API_KEY`, `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL` in HF Space secrets; confirm `/health` returns 200 and a chat message creates a task in Neon DB

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3–7 (User Stories)**: All depend on Phase 2 completion; can proceed in priority order (P1→P5) or in parallel if staffed
- **Phase 8 (History)**: Depends on Phase 3 (POST /chat must exist before adding GET endpoints)
- **Phase 9 (Frontend)**: Depends on Phase 3 (backend /chat endpoint must work first)
- **Phase 10 (Polish)**: Depends on Phase 3–8 completion

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no other story dependencies; delivers standalone MVP
- **US2 (P2)**: After Phase 2 — independent; enhances US1 flow
- **US3 (P3)**: After Phase 2 — independent; works with tasks created by US1
- **US4 (P4)**: After Phase 2 — independent; works with tasks created by US1
- **US5 (P5)**: After Phase 2 — independent; works with tasks created by US1

### Within Each User Story

- MCP tool handler → tool unit tests → chat integration
- Tool handler must exist before agent can dispatch to it
- Commit after each task or logical group

### Parallel Opportunities

```
Phase 2 parallelizable:
  T005 (database.py) ──┐
  T006 (models)      ──┤
  T007 (schemas)     ──┤─→ T008 (auth dep) → T011 (conftest) → T012 (main.py)
  T009 (mcp scaffold)──┤
  T010 (agent scaffold)┘

Phase 3–7: user story phases can be parallelized by developer
  Dev A: T013–T018 (US1 create)
  Dev B: T019–T020 (US2 list)   ← after Phase 2
  Dev C: T021–T022 (US3 complete)
```

---

## Parallel Example: User Story 1

```bash
# After Phase 2 is complete, launch US1 tasks:

# Stream 1: MCP tool + agent
Task: "T013 Implement add_task in backend/services/mcp_tools.py"
Task: "T014 Implement generate_response() in backend/services/ai_agent.py"

# Stream 2 (after T013, T014):
Task: "T015 Create POST /chat endpoint in backend/routes/chat.py"

# Stream 3 (after T013):
Task: "T017 Write add_task unit tests in backend/tests/test_mcp_tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T012) — **CRITICAL**
3. Complete Phase 3: US1 Create Task (T013–T018)
4. **STOP and VALIDATE**: Type "Add buy milk" in chat, verify task created
5. Deploy to HF Space — MVP live

### Incremental Delivery

1. Setup + Foundational → Server starts, `/health` 200
2. US1 → Task creation via chat (MVP!)
3. US2 → Task listing via chat
4. US3 → Task completion via chat
5. US4 → Task deletion via chat
6. US5 → Task updates via chat
7. Phase 8 → Conversation history persists
8. Phase 9 → Frontend ChatKit connected
9. Phase 10 → Tests, isolation, hardening

Each phase delivers working, independently testable functionality.

---

## Task Count Summary

| Phase | Tasks | Parallelizable | User Story |
|-------|-------|---------------|-----------|
| Phase 1: Setup | T001–T003 | T002, T003 | — |
| Phase 2: Foundational | T004–T012 | T005–T010 | — |
| Phase 3: US1 Create | T013–T018 | — | US1 |
| Phase 4: US2 List | T019–T020 | — | US2 |
| Phase 5: US3 Complete | T021–T022 | — | US3 |
| Phase 6: US4 Delete | T023–T024 | — | US4 |
| Phase 7: US5 Update | T025–T026 | — | US5 |
| Phase 8: History | T027–T029 | T028 | — |
| Phase 9: Frontend | T030–T033 | T031, T032 | — |
| Phase 10: Polish | T034–T039 | T034–T036 | — |
| **Total** | **39 tasks** | **16 parallelizable** | — |

---

## Notes

- `[P]` tasks target different files — no merge conflicts when run in parallel
- Each user story phase is independently deployable after Phase 2 completes
- MCP tool handlers in `mcp_tools.py` can be added one at a time (US1→US5) without breaking existing tools
- `MAX_CONTEXT_MESSAGES = 20` in `backend/routes/chat.py` — configurable constant
- Tests use `aiosqlite` in-memory — no Neon DB or OpenAI key needed for CI
- Commit after each task; push after each phase checkpoint
