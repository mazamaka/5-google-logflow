"""add check constraint for logs.level

Revision ID: 7a5b9c2d4e7f
Revises: 3c1d2ea4a91b
Create Date: 2025-09-23 18:45:00.000000

"""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "7a5b9c2d4e7f"
down_revision = "3c1d2ea4a91b"
branch_labels = None
depends_on = None


LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def upgrade() -> None:
    op.execute(
        "ALTER TABLE logs ADD CONSTRAINT ck_logs_level CHECK (level IN ('%s'))" % "','".join(LEVELS)
    )


def downgrade() -> None:
    op.execute("ALTER TABLE logs DROP CONSTRAINT IF EXISTS ck_logs_level")
