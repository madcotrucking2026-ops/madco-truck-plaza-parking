"""payment_method enum — add 'tender_card' and 'house_account'

Two new payment-method labels the plaza takes at the desk. On Postgres the
column is a native enum, so the values are added with ALTER TYPE inside an
autocommit block (ADD VALUE cannot run in the migration's transaction). On
SQLite the SQLAlchemy Enum has no CHECK constraint (create_constraint defaults
to False), so the column already accepts any string — nothing to do. Additive
and safe online.

Revision ID: f3b9d2a7c410
Revises: e2a4c6f80b19
Create Date: 2026-08-09
"""

from alembic import op

revision = "f3b9d2a7c410"
down_revision = "e2a4c6f80b19"
branch_labels = None
depends_on = None

_NEW_VALUES = ("tender_card", "house_account")


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return  # SQLite: plain VARCHAR, no constraint — new values already valid.
    with op.get_context().autocommit_block():
        for value in _NEW_VALUES:
            op.execute(f"ALTER TYPE payment_method ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres cannot drop a value from an enum type; the honest downgrade is a
    # no-op (the extra labels are harmless if unused).
    pass
