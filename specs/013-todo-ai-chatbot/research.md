# Research: Todo AI Chatbot (013-todo-ai-chatbot)

**Date**: 2026-02-21 | **Branch**: `013-todo-ai-chatbot`

---

## 1. FastAPI + Neon DB Connection

**Decision**: Use `SQLModel` with `asyncpg` dialect for async Neon PostgreSQL access. Connection string read from `DATABASE_URL` env var via `pydantic-settings`.

**Rationale**:
- `asyncpg` is the fastest async PostgreSQL driver for Python and is required for FastAPI's async request lifecycle.
- Neon requires `?ssl=require` in the connection string — `asyncpg` handles this natively.
- `SQLModel.metadata.create_all()` at startup is sufficient for this project scale (no Alembic migrations needed until schema changes become frequent).
- `AsyncSession` is yielded per request via a FastAPI dependency (`get_db_session`); sessions are never shared across requests.

**Alternatives considered**:
- `databases` library (asyncio-native SQL) — less integration with SQLModel's ORM features; rejected.
- Synchronous `psycopg2` — blocks the event loop; rejected.

---

## 2. Official MCP SDK Tool Registration

**Decision**: Use `FastMCP` from the official MCP Python SDK (`mcp >= 1.26.0`) with `@server.tool()` decorator pattern. Transport: `stdio` subprocess.

**Rationale**:
- `FastMCP` generates JSON schema from Python type annotations automatically — no manual schema maintenance.
- `@server.tool()` docstrings serve as tool descriptions for the model, directly influencing when the model calls each tool.
- Stdio transport is the simplest and most reliable for co-located backend deployments — no extra ports or auth needed.
- Each tool opens its own DB session (`_get_db_session()` context manager) because tools execute in a subprocess context, separate from the FastAPI request session.

**Alternatives considered**:
- HTTP-based MCP transport — adds port management and latency; rejected for co-located deployment.
- Manual tool schema registration (raw JSON) — brittle, harder to maintain; rejected.
- LangChain tools — heavyweight dependency with different abstractions; rejected.

---

## 3. OpenAI Agents SDK Integration

**Decision**: Use `openai-agents` SDK (`Runner.run`) with `MCPServerStdio` for the main backend. The SDK handles the multi-round tool-call loop automatically.

**Rationale**:
- `Runner.run(agent, messages)` drives the agentic loop internally — the SDK calls the model, detects tool calls, dispatches them via MCP, feeds results back, and repeats until `end_turn`. This eliminates ~50 lines of manual loop management.
- `MCPServerStdio` spawns `mcp_tools.py` as a subprocess, providing clean process isolation between the FastAPI event loop and tool execution.
- `cache_tools_list=True` avoids re-fetching the tool schema from the subprocess on every request.
- `user_id` is injected into the system prompt by `AIAgentService`, not extracted from user messages — the model cannot claim a different user's ID.

**Alternatives considered**:
- Manual loop with raw `openai.chat.completions.create` — viable but requires ~50 lines of loop management per request; rejected in favour of SDK.
- Anthropic SDK with tool use — valid but requires different loop logic; reserved for HF Space.
- Direct function dispatch (no MCP subprocess) — used in HF Space where subprocess spawning is unreliable in the free tier sandbox.

---

## 4. ChatKit UI → `/api/{user_id}/chat` Connection

**Decision**: ChatKit (Next.js) posts to `POST /api/v1/users/{user_id}/chat` with a Bearer JWT. Vercel rewrites proxy `/api/*` to the HF Space backend URL. `conversation_id` is managed in frontend React state.

**Rationale**:
- Vercel rewrites (`vercel.json`) allow the frontend to call `/api/*` without CORS issues — requests appear same-origin from the browser's perspective.
- Bearer JWT is attached by `apiClient()` (`lib/api-client.ts`) from Better Auth's `getAuthToken()`.
- The `conversation_id` returned by the first response is stored in state and sent with all subsequent messages in the same session.
- On `conversation_id: null`, the backend creates a new conversation and returns its UUID.

**Alternatives considered**:
- WebSockets for streaming — adds complexity; the current AI response latency is dominated by model inference, not transport; rejected for this phase.
- Server-sent events (SSE) — viable for streaming text; deferred to a future iteration.

---

## 5. Database Schema — Primary Key Type

**Decision**: UUID primary keys (`uuid4()` generated in Python) for all tables.

**Rationale**:
- UUIDs prevent task ID enumeration attacks (users cannot guess adjacent task IDs by incrementing an integer).
- `uuid4()` is generated client-side (Python), avoiding a DB round-trip for the default.
- Neon PostgreSQL stores UUIDs natively as a 16-byte type.
- `owner_id` (not `user_id`) is the column name for the Better Auth user reference — avoids SQL reserved word ambiguity and makes ownership semantics explicit.

---

## 6. Conversation Context Window

**Decision**: Load the last **20** messages per request (not the spec's stated 5–10).

**Rationale**:
- Each exchange produces 2 messages (user + assistant). 10 messages = 5 exchanges — too shallow for multi-step flows (e.g., list → update → list again = 3 exchanges × 2 = 6 messages).
- 20 messages = 10 full exchanges, sufficient for typical task management sessions while staying well within model context limits.
- Defined as `MAX_CONTEXT_MESSAGES = 20` in `backend/routes/chat.py` — configurable without code changes.

---

## 7. Tool Call Persistence

**Decision**: Persist every tool invocation (`tool_name`, `parameters`, `result`, `status`) in a `tool_calls` table linked to the assistant message via `message_id` FK.

**Rationale**:
- Enables full audit trail — operators can trace exactly what the AI did in response to each user message.
- Supports debugging unexpected agent behaviour.
- The causal chain is preserved: user message → assistant message → tool calls.

---

## 8. Error Handling

**Decision**: AI agent exceptions → HTTP 502; tool call errors (`is_error: true`) → agent translates to conversational natural-language response.

**Rationale**:
- Tool failures (task not found, validation error) are in-domain events the user can act on — the AI delivers them as friendly messages.
- Agent-level failures (model unavailable, API key error) are infrastructure problems — they surface as HTTP 502 since the user cannot resolve them via conversation.
- User message is persisted **before** the AI call, so it is never lost even if the model times out or errors.
