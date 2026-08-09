"""payments.reversal_of_payment_id — link a void's reversal entry to its original

Voiding a mistaken payment records a negative reversal entry rather than
deleting anything (payments are permanent). This nullable self-reference points
the reversal at the payment it cancels, so a payment can be marked "voided" and
never double-voided. Additive — a safe online migration.

Revision ID: e2a4c6f80b19
Revises: d4e8b1c2f9a3
Create Date: 2026-08-09
"""

import sqlalchemy as sa
from alembic import op

revision = "e2a4c6f80b19"
down_revision = "d4e8b1c2f9a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("reversal_of_payment_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("payments", "reversal_of_payment_id")
