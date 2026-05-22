"""add_party_slug

Revision ID: 20260522_000001
Revises: 20260521_000001
Create Date: 2026-05-22 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260522_000001"
down_revision: Union[str, None] = "20260521_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add slug column as nullable first so existing rows are unaffected
    op.add_column("parties", sa.Column("slug", sa.String(200), nullable=True))

    # 2. Set explicit slugs for the 4 known seed parties by name_hy match
    op.execute(
        "UPDATE parties SET slug = 'qaghaqaciakan-paymanagir' "
        "WHERE name_hy = 'Քաղաքացիական պայմանագիր'"
    )
    op.execute(
        "UPDATE parties SET slug = 'hay-heghapokhakan-dashnaktsutyun' "
        "WHERE name_hy = 'Հայ Հեղափոխական Դաշնակցություն'"
    )
    op.execute(
        "UPDATE parties SET slug = 'bargavaj-hayastan' "
        "WHERE name_hy = 'Բարգավաճ Հայաստան'"
    )
    op.execute(
        "UPDATE parties SET slug = 'hayastani-hanrapetakan-kusaktsutyun' "
        "WHERE name_hy = 'Հայաստանի Հանրապետական կուսակցություն'"
    )

    # 3. Enforce NOT NULL after data is populated
    op.alter_column("parties", "slug", nullable=False)

    # 4. Add unique constraint
    op.create_unique_constraint("uq__parties__slug", "parties", ["slug"])


def downgrade() -> None:
    op.drop_constraint("uq__parties__slug", "parties", type_="unique")
    op.drop_column("parties", "slug")
