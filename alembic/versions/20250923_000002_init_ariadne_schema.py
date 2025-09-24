"""init ariadne schema (automation_runs, logs)

Revision ID: 3c1d2ea4a91b
Revises: 6c8fab1b3f1a
Create Date: 2025-09-23 14:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3c1d2ea4a91b"
down_revision = "6c8fab1b3f1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # На случай, если уже есть старая таблица logs — удаляем
    op.execute("DROP TABLE IF EXISTS logs CASCADE")

    # automation_runs
    op.create_table(
        "automation_runs",
        sa.Column("run_id", sa.String(length=255), primary_key=True, nullable=False),
        sa.Column("task_id", sa.String(length=255), nullable=False),
        sa.Column("profile_id", sa.String(length=255), nullable=True),
        sa.Column("action_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'running'")),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_runs_task_id", "automation_runs", ["task_id"], unique=False)

    # logs
    op.create_table(
        "logs",
        sa.Column("log_id", postgresql.BIGINT(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=255), sa.ForeignKey("automation_runs.run_id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=False),
    )
    op.create_index("idx_logs_run_id_timestamp", "logs", ["run_id", "timestamp"], unique=False)
    op.create_index("idx_logs_data_gin", "logs", ["data"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("idx_logs_data_gin", table_name="logs")
    op.drop_index("idx_logs_run_id_timestamp", table_name="logs")
    op.drop_table("logs")
    op.drop_index("idx_runs_task_id", table_name="automation_runs")
    op.drop_table("automation_runs")
