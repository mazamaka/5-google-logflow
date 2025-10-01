"""add task_data to automation_runs

Revision ID: 9f2d3c4b5a6e
Revises: 7a5b9c2d4e7f
Create Date: 2025-10-01 19:55:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9f2d3c4b5a6e"
down_revision = "7a5b9c2d4e7f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "automation_runs",
        sa.Column("task_data", postgresql.JSONB(), nullable=True),
    )
    # Индекс GIN по JSONB колонке, чтобы поддержать потенциальные запросы по task_data
    op.create_index(
        "idx_runs_task_data_gin",
        "automation_runs",
        ["task_data"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("idx_runs_task_data_gin", table_name="automation_runs")
    op.drop_column("automation_runs", "task_data")
