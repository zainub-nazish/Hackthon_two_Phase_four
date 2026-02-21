# Data Model: Todo AI Chatbot (013-todo-ai-chatbot)

**Date**: 2026-02-21 | **Branch**: `013-todo-ai-chatbot`

---

## Entity Relationship Overview

```
User (Better Auth — external, not a SQLModel table)
  │
  ├──< Task (owner_id → user.id)
  │
  └──< Conversation (owner_id → user.id)
          │
          └──< Message (conversation_id → Conversation.id)
                  │
                  └──< ToolCall (message_id → Message.id)
```

`owner_id` is a plain string column (JWT `sub` claim). No FK constraint to the `users` table because Better Auth manages users in a separate auth context. Ownership is enforced at the application layer — every query filters by `owner_id == user_id`.

---

## Entities

### Task

Represents a single to-do item owned by a user.

| Field       | Type       | Constraints                 | Notes                                  |
|-------------|------------|-----------------------------|----------------------------------------|
| id          | UUID       | PK, default uuid4()         | System-generated, opaque to users      |
| owner_id    | str        | NOT NULL, indexed           | Better Auth user ID (JWT `sub` claim)  |
| title       | str        | NOT NULL, max 200 chars     | Required; stripped of whitespace       |
| description | str / NULL | max 2000 chars              | Optional detail or notes               |
| completed   | bool       | NOT NULL, default False     | True once user marks task done         |
| created_at  | datetime   | NOT NULL, default utcnow()  | Set on insert, never updated           |
| updated_at  | datetime   | NOT NULL, default utcnow()  | Updated on every mutation              |

**Validation rules**:
- `title` must be non-empty after stripping whitespace
- `description` is optional; if provided, max 2000 characters
- `completed` is one-directional — only `False → True` (no un-completing in this phase)

**State transitions**:
```
pending (completed=False) ──complete_task──► completed (completed=True)
```

---

### Conversation

Represents a persistent chat session belonging to one user.

| Field      | Type     | Constraints                | Notes                                     |
|------------|----------|----------------------------|-------------------------------------------|
| id         | UUID     | PK, default uuid4()        | Returned to frontend on first message     |
| owner_id   | str      | NOT NULL, indexed          | Better Auth user ID                       |
| created_at | datetime | NOT NULL, default utcnow() | Immutable after creation                  |
| updated_at | datetime | NOT NULL, default utcnow() | Bumped on every new message exchange      |

**Notes**:
- Created automatically when `conversation_id` is null in a chat request.
- `updated_at` is sorted descending to retrieve the user's most recent conversation.
- One user may have multiple conversations; history is preserved across sessions.

---

### Message

A single turn in a conversation — either from the user or the assistant.

| Field           | Type     | Constraints                           | Notes                               |
|-----------------|----------|---------------------------------------|-------------------------------------|
| id              | UUID     | PK, default uuid4()                   |                                     |
| conversation_id | UUID     | NOT NULL, FK → conversations.id, idx  | Parent conversation                 |
| role            | str      | NOT NULL, max 20 chars                | `"user"` or `"assistant"`           |
| content         | str      | NOT NULL                              | Full text of the message turn       |
| created_at      | datetime | NOT NULL, default utcnow()            | Used for chronological ordering     |

**Context window**: The last 20 messages (by `created_at DESC LIMIT 20`, then reversed) are sent as AI context per request. Constant: `MAX_CONTEXT_MESSAGES = 20`.

---

### ToolCall

Records every MCP tool invocation made by the AI agent in a single assistant turn.

| Field      | Type     | Constraints                       | Notes                                       |
|------------|----------|-----------------------------------|---------------------------------------------|
| id         | UUID     | PK, default uuid4()               |                                             |
| message_id | UUID     | NOT NULL, FK → messages.id, idx   | The assistant message that triggered this   |
| tool_name  | str      | NOT NULL, max 100 chars           | e.g. `add_task`, `complete_task`            |
| parameters | str      | NOT NULL                          | JSON-encoded input arguments                |
| result     | str      | NOT NULL                          | JSON-encoded output or error                |
| status     | str      | NOT NULL, max 20 chars            | `"success"` or `"error"`                    |
| created_at | datetime | NOT NULL, default utcnow()        | Execution timestamp                         |

---

## MCP Tool Signatures

All tools enforce user isolation — `user_id` is injected by the agent service from the system prompt, not read from user input.

| Tool          | Inputs                                                           | Returns on success                             | Returns on error                     |
|---------------|------------------------------------------------------------------|------------------------------------------------|--------------------------------------|
| add_task      | title (str), user_id (str), description? (str)                   | `{id, title, description, completed}`          | `{is_error: true, error: str}`       |
| list_tasks    | user_id (str), status? ("all"/"pending"/"completed")             | `{tasks: [{id,title,description,completed}], count: int}` | `{is_error: true, error: str}` |
| complete_task | task_id (str UUID), user_id (str)                                | `{id, title, completed: true}`                 | `{is_error: true, error: str}`       |
| delete_task   | task_id (str UUID), user_id (str)                                | `{success: true, deleted_task_id: str}`        | `{is_error: true, error: str}`       |
| update_task   | task_id (str UUID), user_id (str), title? (str), description? (str) | `{id, title, description, completed}`      | `{is_error: true, error: str}`       |

**Error handling**: The agent translates `is_error` results into conversational natural-language responses — tool errors never surface as HTTP errors to the client.

---

## Database Tables (DDL Summary)

```sql
-- Managed by SQLModel — created at startup via SQLModel.metadata.create_all()

CREATE TABLE tasks (
    id          UUID         PRIMARY KEY,
    owner_id    VARCHAR      NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    completed   BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP    NOT NULL,
    updated_at  TIMESTAMP    NOT NULL
);
CREATE INDEX ix_tasks_owner_id ON tasks(owner_id);

CREATE TABLE conversations (
    id          UUID      PRIMARY KEY,
    owner_id    VARCHAR   NOT NULL,
    created_at  TIMESTAMP NOT NULL,
    updated_at  TIMESTAMP NOT NULL
);
CREATE INDEX ix_conversations_owner_id ON conversations(owner_id);

CREATE TABLE messages (
    id              UUID         PRIMARY KEY,
    conversation_id UUID         NOT NULL REFERENCES conversations(id),
    role            VARCHAR(20)  NOT NULL,
    content         TEXT         NOT NULL,
    created_at      TIMESTAMP    NOT NULL
);
CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);

CREATE TABLE tool_calls (
    id          UUID          PRIMARY KEY,
    message_id  UUID          NOT NULL REFERENCES messages(id),
    tool_name   VARCHAR(100)  NOT NULL,
    parameters  TEXT          NOT NULL,
    result      TEXT          NOT NULL,
    status      VARCHAR(20)   NOT NULL,
    created_at  TIMESTAMP     NOT NULL
);
CREATE INDEX ix_tool_calls_message_id ON tool_calls(message_id);
```
