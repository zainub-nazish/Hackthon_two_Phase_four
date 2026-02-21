# Quickstart: Todo AI Chatbot (013-todo-ai-chatbot)

**Date**: 2026-02-21 | **Branch**: `013-todo-ai-chatbot`

---

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database (connection string with `?ssl=require`)
- OpenAI API key (`sk-proj-...` or `sk-...`)
- Node.js 18+ (for frontend)

---

## 1. Backend Setup (FastAPI + Neon DB)

```bash
# Clone and enter project
git clone <repo-url>
cd phase_three

# Create virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname?ssl=require
BETTER_AUTH_SECRET=your-secret-here
OPENAI_API_KEY=sk-...
```

```bash
# Start the server (tables created automatically on startup)
uvicorn backend.main:app --reload --port 8000
```

- API docs (debug mode): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

## 2. MCP Tools (Official MCP SDK)

Tools are defined in `backend/services/mcp_tools.py` using `FastMCP`. They run as a stdio subprocess when the AI agent is invoked. No separate startup is needed — the agent service spawns the subprocess automatically.

To inspect available tools manually:

```bash
python backend/services/mcp_tools.py
# Starts MCP server in stdio mode — Ctrl+C to exit
```

Five tools are registered:
- `add_task` — create a new task
- `list_tasks` — list tasks with optional status filter
- `complete_task` — mark a task done by UUID
- `delete_task` — permanently delete a task by UUID
- `update_task` — update title and/or description by UUID

---

## 3. OpenAI Agents SDK (AI Reasoning Loop)

The agentic loop is in `backend/services/ai_agent.py`. It:
1. Loads the five MCP tools from the subprocess
2. Builds the system prompt with the user's `user_id` injected
3. Calls `Runner.run(agent, messages)` — the SDK handles multi-round tool calls
4. Returns the final `AgentResponse` with `content` and `tool_calls[]`

No separate configuration is needed beyond `OPENAI_API_KEY` in `.env`.

---

## 4. Running Tests

```bash
# From project root
pytest backend/tests/ -v

# Run only chat endpoint tests
pytest backend/tests/test_chat.py -v

# Run only MCP tool tests
pytest backend/tests/test_mcp_tools.py -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

Tests use `aiosqlite` (in-memory SQLite) — no real database or API key needed.

---

## 5. Frontend Setup (ChatKit UI)

```bash
cd frontend
npm install

cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev   # http://localhost:3000
```

The chat page is at `http://localhost:3000/chat`. Sign in first — chat requires a valid session.

---

## 6. Sending a Chat Message (cURL)

```bash
TOKEN="your-jwt-token"
USER_ID="your-user-id"
BASE="http://localhost:8000"

# Start a new conversation
curl -X POST "$BASE/api/v1/users/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries to my list"}'

# Response:
# {
#   "conversation_id": "a5308f26-...",
#   "response": "Done! I've added 'Buy groceries' to your task list.",
#   "tool_calls": [{"tool_name": "add_task", "status": "success", ...}]
# }

# Continue the same conversation
curl -X POST "$BASE/api/v1/users/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my pending tasks", "conversation_id": "a5308f26-..."}'

# Mark a task done
curl -X POST "$BASE/api/v1/users/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "I finished the groceries", "conversation_id": "a5308f26-..."}'
```

---

## 7. Key Source Files

| File | Purpose |
|------|---------|
| `backend/routes/chat.py` | Chat endpoints: `POST /chat`, `GET /conversations`, `GET /messages` |
| `backend/services/ai_agent.py` | Agentic loop — OpenAI Agents SDK + MCP stdio |
| `backend/services/mcp_tools.py` | MCP tool handlers (add/list/complete/delete/update) |
| `backend/models/database.py` | SQLModel table definitions: Task, Conversation, Message, ToolCall |
| `backend/models/schemas.py` | Pydantic request/response schemas |
| `backend/auth/dependencies.py` | `verify_user_owns_resource` — JWT auth + user isolation |
| `backend/database.py` | Async engine + session factory |
| `frontend/src/app/(dashboard)/chat/` | ChatKit UI page |
| `frontend/lib/api-client.ts` | `apiClient()` — attaches Bearer token to every request |

---

## 8. Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://...?ssl=require` |
| `BETTER_AUTH_SECRET` | Yes | Secret for JWT verification |
| `OPENAI_API_KEY` | Yes | OpenAI key for the agentic loop |
| `BETTER_AUTH_URL` | Yes (production) | Better Auth server URL |
| `DEBUG` | No | Set `true` to enable `/docs` in production |
