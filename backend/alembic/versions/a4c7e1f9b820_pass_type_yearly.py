"""pass_type enum — add 'yearly'

A yearly parking pass (12-month term, custom flat annual price, reserved spot in
the monthly zone). On Postgres pass_type is a native enum, so the value is added
with ALTER TYPE in an autocommit block (ADD VALUE can't run in the migration's
transaction). On SQLite the Enum has no CHECK constraint, so nothing to do.

Revision ID: a4c7e1f9b820
Revises: f3b9d2a7c410
Create Date: 2026-08-09
"""

from alembic import op

revision = "a4c7e1f9b820"
down_revision = "f3b9d2a7c410"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE pass_type ADD VALUE IF NOT EXISTS 'yearly'")


def downgrade() -> None:
    # Postgres cannot drop an enum value; a no-op is the honest downgrade.
    pass
