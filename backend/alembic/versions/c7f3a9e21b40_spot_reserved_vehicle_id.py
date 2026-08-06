"""spot reserved_vehicle_id — fixed monthly spot reservation

Adds a nullable FK from a spot to the vehicle (monthly truck) that OWNS it. A
reserved spot is held for that truck even while it's empty and is out of the
daily pool. Additive + nullable, so it is a safe online migration.

Revision ID: c7f3a9e21b40
Revises: b5d73c339fd1
Create Date: 2026-08-06
"""

import sqlalchemy as sa
from alembic import op

revision = "c7f3a9e21b40"
down_revision = "b5d73c339fd1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Batch mode + a NAMED FK: SQLite has no ALTER-ADD-CONSTRAINT, so alembic
    # rebuilds the table, and an unnamed FK breaks that rebuild.
    with op.batch_alter_table("spots", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reserved_vehicle_id", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_spots_reserved_vehicle_id"), ["reserved_vehicle_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_spots_reserved_vehicle_id_vehicles", "vehicles", ["reserved_vehicle_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("spots", schema=None) as batch_op:
        batch_op.drop_constraint("fk_spots_reserved_vehicle_id_vehicles", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_spots_reserved_vehicle_id"))
        batch_op.drop_column("reserved_vehicle_id")
