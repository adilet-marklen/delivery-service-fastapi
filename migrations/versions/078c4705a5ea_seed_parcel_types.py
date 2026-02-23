"""seed parcel types

Revision ID: 078c4705a5ea
Revises: c2da0bc43172
Create Date: 2026-02-23 00:02:25.398062

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "078c4705a5ea"
down_revision: str | None = "c2da0bc43172"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    parcel_types_table = sa.table(
        "parcel_types",
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        parcel_types_table,
        [
            {"name": "clothes"},
            {"name": "electronics"},
            {"name": "other"},
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM parcel_types WHERE name IN ('clothes', 'electronics', 'other')")
    )
