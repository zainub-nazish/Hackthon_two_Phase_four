# ============================================================
# Task ID  : T009
# Title    : Add audit_log and event_dedup tables
# Spec Ref : speckit.tasks → T009 (audit + dedup migration)
# Plan Ref : speckit.plan → Section 3.4: Idempotency enforcement
# ============================================================
"""Add audit_log and event_dedup tables for Phase V event sourcing

Revision ID: 002
Revises: 001
Create Date: 2026-03-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Immutable audit log — one row per Kafka event consumed by any service
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(36), primary_key=True),          # UUID
        sa.Column("event_id", sa.String(36), nullable=False, unique=True),  # Kafka dedup key
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_event_type", "audit_log", ["event_type"])
    op.create_index("ix_audit_log_topic", "audit_log", ["topic"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    # Event deduplication table — used by ALL consumer services
    # Primary key = event_id ensures insert fails on duplicate (idempotency guard)
    op.create_table(
        "event_dedup",
        sa.Column("event_id", sa.String(36), primary_key=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service", sa.String(50), nullable=False),        # which service processed it
    )


def downgrade() -> None:
    op.drop_table("event_dedup")
    op.drop_index("ix_audit_log_created_at", "audit_log")
    op.drop_index("ix_audit_log_topic", "audit_log")
    op.drop_index("ix_audit_log_event_type", "audit_log")
    op.drop_table("audit_log")
