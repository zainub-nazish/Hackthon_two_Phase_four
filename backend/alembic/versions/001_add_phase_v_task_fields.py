# ============================================================
# Task ID  : T008
# Title    : Add Phase V task fields migration
# Spec Ref : speckit.tasks → T011 (Task model extension)
# Plan Ref : speckit.plan → Section 2.4: Database & External Services
# ============================================================
"""Add Phase V task fields: due_date, priority, tags, recurrence, completed_at

Revision ID: 001
Revises: None
Create Date: 2026-03-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add due_date — nullable datetime
    op.add_column(
        "tasks",
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
    )
    # Add priority — enum-like string with default 'medium'
    op.add_column(
        "tasks",
        sa.Column("priority", sa.String(length=10), nullable=False, server_default="medium"),
    )
    # Add tags — JSON array stored as TEXT (SQLite) or JSON (PostgreSQL)
    op.add_column(
        "tasks",
        sa.Column("tags", sa.JSON(), nullable=True, server_default="[]"),
    )
    # Add recurrence — JSON object: {interval, every} or null
    op.add_column(
        "tasks",
        sa.Column("recurrence", sa.JSON(), nullable=True),
    )
    # Add completed_at — set when task is explicitly completed via /complete endpoint
    op.add_column(
        "tasks",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tasks", "completed_at")
    op.drop_column("tasks", "recurrence")
    op.drop_column("tasks", "tags")
    op.drop_column("tasks", "priority")
    op.drop_column("tasks", "due_date")
