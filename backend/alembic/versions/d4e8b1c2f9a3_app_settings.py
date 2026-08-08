"""app_settings — owner-editable config (parking capacity + default prices)

A tiny key/value table whose rows OVERRIDE the env/config defaults at runtime.
Additive, so it is a safe online migration.

Revision ID: d4e8b1c2f9a3
Revises: c7f3a9e21b40
Create Date: 2026-08-08
"""

import sqlalchemy as sa
from alembic import op

revision = "d4e8b1c2f9a3"
down_revision = "c7f3a9e21b40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
