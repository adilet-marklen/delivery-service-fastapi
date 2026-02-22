"""create parcels and parcel types

Revision ID: c2da0bc43172
Revises:
Create Date: 2026-02-22 23:54:15.696537

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c2da0bc43172"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "parcel_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "parcels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("weight_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("declared_cost_usd", sa.Numeric(12, 2), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("delivery_cost_rub", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["type_id"], ["parcel_types.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_parcels_user_id", "parcels", ["user_id"], unique=False)
    op.create_index("ix_parcels_type_id", "parcels", ["type_id"], unique=False)
    op.create_index(
        "ix_parcels_unprocessed_delivery_cost",
        "parcels",
        ["delivery_cost_rub"],
        unique=False,
        postgresql_where=sa.text("delivery_cost_rub IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_parcels_unprocessed_delivery_cost", table_name="parcels")
    op.drop_index("ix_parcels_type_id", table_name="parcels")
    op.drop_index("ix_parcels_user_id", table_name="parcels")
    op.drop_table("parcels")
    op.drop_table("parcel_types")
