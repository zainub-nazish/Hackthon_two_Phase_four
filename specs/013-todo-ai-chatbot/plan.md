# Implementation Plan: Todo AI Chatbot (013-todo-ai-chatbot)

**Branch**: `013-todo-ai-chatbot` | **Date**: 2026-02-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-todo-ai-chatbot/spec.md`

---

## Summary

Build a stateless, database-backed AI chat system that lets authenticated users manage tasks through natural conversation. The system is structured around four integration layers:

1. **FastAPI + Neon DB** — async HTTP backend connected to Neon PostgreSQL via asyncpg
2. **Official MCP SDK** — five task tools (`add`, `list`, `complete`, `delete`, `update`) registered via `FastMCP` and exposed over stdio transport
3. **OpenAI Agents SDK** — agentic loop (`Runner.run`) that reasons over user messages, dispatches MCP tool calls autonomously, and returns a final natural-language response
4. **ChatKit UI → `/api/{user_id}/chat`** — Next.js frontend posts messages with Bearer auth; each turn persists both user and assistant messages to Neon DB

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript / Next.js 15 (frontend)
**Primary Dependencies**:
- FastAPI + Uvicorn (HTTP server)
- SQLModel + asyncpg (async ORM + PostgreSQL driver)
- `openai-agents >= 0.0.7` (agentic loop with MCP)
- `mcp >= 1.26.0` (official MCP Python SDK, FastMCP, stdio transport)
- `pydantic-settings` (env config)
- `python-jose[cryptography]` (JWT verification)
- `aiosqlite` (in-memory SQLite for tests)

**Storage**: Neon PostgreSQL — asyncpg dialect, SSL required
**Testing**: pytest + pytest-asyncio + httpx
**Target Platform**: Linux server (HF Space Docker), Vercel (frontend)
**Performance Goals**: AI response < 10 seconds p95 (dominated by model inference latency)
**Constraints**: No in-memory state — all reads/writes to Neon DB. User isolation enforced at every DB query.
**Scale/Scope**: Single user per conversation, ~10K total users

---

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| No hardcoded secrets | ✅ PASS | API keys read from env via `pydantic-settings` |
| User isolation enforced | ✅ PASS | All queries filter `owner_id == user_id`; tool injection is server-side |
| No in-memory state | ✅ PASS | All persistence via Neon DB; user message saved before AI call |
| Tests required | ✅ PASS | pytest suite: `test_chat.py`, `test_mcp_tools.py`, `test_ai_agent.py`, `test_chat_isolation.py` |
| Smallest viable diff | ✅ PASS | Plan extends existing backend structure, no rewrites |
| Auth on all endpoints | ✅ PASS | `verify_user_owns_resource` dependency on all `/api/v1/users/{user_id}/*` routes |

No violations requiring justification.

---

## Project Structure

### Documentation (this feature)

```text
specs/013-todo-ai-chatbot/
├── plan.md              ← this file
├── research.md          ← Phase 0: decisions and rationale
├── data-model.md        ← Phase 1: entity definitions and DDL
├── quickstart.md        ← Phase 1: local dev and test instructions
├── contracts/
│   ├── chat-api.yaml    ← Phase 1: OpenAPI 3.1 contract
│   └── mcp-tools.yaml   ← Phase 1: MCP tool contract
└── tasks.md             ← Phase 2 output (/sp.tasks — not yet created)
```

### Source Code

```text
backend/                              ← Main backend (FastAPI)
├── main.py                           # App entry, CORS, router registration
├── config.py                         # Settings (OPENAI_API_KEY, DATABASE_URL, etc.)
├── database.py                       # Async engine, session factory
├── auth/
│   └── dependencies.py               # verify_user_owns_resource (JWT → CurrentUser)
├── models/
│   ├── database.py                   # Task, Conversation, Message, ToolCall (SQLModel)
│   └── schemas.py                    # ChatRequest, ChatResponse, MessageResponse, etc.
├── routes/
│   └── chat.py                       # POST /chat, GET /conversations, GET /messages
├── services/
│   ├── ai_agent.py                   # Agentic loop (OpenAI Agents SDK + MCP stdio)
│   └── mcp_tools.py                  # @server.tool() handlers (FastMCP)
└── tests/
    ├── conftest.py                    # Fixtures: test app, DB override, auth stub
    ├── test_chat.py                   # Integration: POST /chat scenarios
    ├── test_chat_isolation.py         # Security: cross-user isolation
    ├── test_mcp_tools.py              # Unit: each MCP tool handler
    └── test_ai_agent.py              # Unit: agent stub + tool dispatch

frontend/                             ← Next.js 15
├── src/app/(dashboard)/
│   └── chat/                         # ChatKit UI page
└── lib/api-client.ts                 # apiClient() — attaches Bearer token
```

**Structure Decision**: Web application (Option 2) — separate backend and frontend sub-projects sharing the same git repository.

---

## Architecture Decisions

### AD-1: FastAPI + Neon DB Connection

- `DATABASE_URL` is read from `.env` via `pydantic-settings`.
- SQLModel creates an async engine with `asyncpg` dialect and `?ssl=require`.
- `get_session()` yields an `AsyncSession` per request; chat routes use `get_db_session()` dependency.
- Tables are created at startup via `SQLModel.metadata.create_all()` in `backend/database.py`.

### AD-2: MCP SDK Tool Registration

- Tools are implemented as `@server.tool()` decorated async functions in `backend/services/mcp_tools.py` using `FastMCP("todo-tools")`.
- Each tool opens its own DB session (tools run in a stdio subprocess, separate from the FastAPI event loop).
- `user_id` is injected by the agent from the system prompt — not trusted from user input.
- Transport: `stdio` (subprocess) for the main backend.

### AD-3: OpenAI Agents SDK Agentic Loop

- `AIAgentService.generate_response()` calls `Runner.run(agent, messages, context=user_id)`.
- `MCPServerStdio` spawns `mcp_tools.py` as a child process with `cache_tools_list=True`.
- The SDK handles multi-round tool calls automatically until the model emits `end_turn`.
- On exception: HTTP 502 returned; user message already persisted.

### AD-4: ChatKit → `/api/{user_id}/chat` Connection

- Frontend calls `POST /api/v1/users/{user_id}/chat` with Bearer JWT.
- Vercel rewrites proxy `/api/*` to the HF Space backend URL.
- `conversation_id` is stored in frontend state; null on first message (creates new conversation).
- Response includes `conversation_id`, `response` text, and `tool_calls[]` for optional display.

### AD-5: Message Persistence Order

1. User message persisted **before** AI call (never lost on timeout).
2. Last 20 messages loaded as context window.
3. Assistant message + tool calls persisted **after** AI returns.
4. On AI exception: conversation timestamp updated, HTTP 502 returned.

---

## Phase 0: Research

✅ Complete — see [research.md](research.md).

Key decisions resolved:
- UUID PKs — prevents task ID enumeration
- `owner_id` column name — avoids SQL keyword collision, explicit ownership semantics
- 20-message context window — covers 10 full user/assistant exchanges
- MCP stdio for main backend; direct function dispatch for HF Space (subprocess not reliable in HF free tier)
- Tool call persistence via `ToolCall` table for full audit trail
- AI errors surface as HTTP 502; tool errors translated by agent to natural language

---

## Phase 1: Design & Contracts

✅ Complete — artifacts:

| Artifact | Path | Status |
|----------|------|--------|
| Data model | [data-model.md](data-model.md) | Done |
| Chat API contract | [contracts/chat-api.yaml](contracts/chat-api.yaml) | Done |
| MCP tools contract | [contracts/mcp-tools.yaml](contracts/mcp-tools.yaml) | Done |
| Quickstart guide | [quickstart.md](quickstart.md) | Done |

---

## Phase 2: Tasks

➡️ Run `/sp.tasks` to generate [tasks.md](tasks.md).

**Scope for tasks.md**:
1. FastAPI app setup — DB engine, session factory, CORS, health endpoint
2. SQLModel table definitions — Task, Conversation, Message, ToolCall
3. MCP tool handlers — add/list/complete/delete/update with user isolation
4. AI agent service — OpenAI Agents SDK loop + MCP stdio integration
5. Chat routes — POST /chat, GET /conversations, GET /messages
6. Auth dependency — `verify_user_owns_resource` (JWT → CurrentUser)
7. Test suite — unit + integration + isolation tests
8. Frontend connection — ChatKit page + API client wiring

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenAI API key missing/invalid | High | High | `/health` endpoint checks key; clear error on startup |
| MCP subprocess timeout in production | Medium | Medium | `client_session_timeout_seconds=30`; HF Space uses direct dispatch as fallback |
| Context window too large (token overflow) | Low | Medium | 20-message limit is well within model context; configurable via `MAX_CONTEXT_MESSAGES` |
| Cross-user data leak | Low | Critical | Every DB query enforces `owner_id == user_id`; isolation tests required |

---

## Open Questions

- Should completed tasks be un-completable? Spec implies no — `complete_task` is one-directional. Confirm before tasks.
- Should the ChatKit UI display tool call details? Currently hidden — confirm UX preference.
