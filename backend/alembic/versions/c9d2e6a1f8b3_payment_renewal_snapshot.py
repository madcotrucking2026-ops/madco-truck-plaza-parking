"""payments: pre-renewal snapshot (prev_issue_date / prev_expiration_date / prev_price)

A renewal payment records the pass's state BEFORE the renewal, so voiding that
payment can roll the pass back to where it was (undo the renewal) rather than
only reversing the money. All nullable + additive — a safe online migration.

Revision ID: c9d2e6a1f8b3
Revises: a4c7e1f9b820
Create Date: 2026-08-11
"""

import sqlalchemy as sa
from alembic import op

revision = "c9d2e6a1f8b3"
down_revision = "a4c7e1f9b820"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("prev_issue_date", sa.Date(), nullable=True))
    op.add_column("payments", sa.Column("prev_expiration_date", sa.Date(), nullable=True))
    op.add_column("payments", sa.Column("prev_price", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("payments", "prev_price")
    op.drop_column("payments", "prev_expiration_date")
    op.drop_column("payments", "prev_issue_date")
