"""add_promise_edits

Revision ID: 20260524_000001
Revises: 20260523_000001
Create Date: 2026-05-24 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as pgENUM

# revision identifiers, used by Alembic.
revision: str = "20260524_000001"
down_revision: Union[str, None] = "20260523_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. promise_edits — full snapshot of editable fields awaiting admin review
    #    moderation_status uses create_type=False because the enum already exists
    #    in PostgreSQL (created by the initial migration for the promises table).
    op.create_table(
        "promise_edits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "promise_id",
            sa.UUID(),
            sa.ForeignKey("promises.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "submitted_by",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "moderation_status",
            pgENUM("pending", "approved", "rejected", name="moderation_status", create_type=False),
            nullable=False,
        ),
        sa.Column("title_hy", sa.String(500), nullable=False),
        sa.Column("quote_hy", sa.Text(), nullable=False),
        sa.Column("description_hy", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("made_date", sa.Date(), nullable=True),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promise_edits")),
    )

    # 2. promise_edit_election_links — M2M between promise_edits and elections
    op.create_table(
        "promise_edit_election_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "edit_id",
            sa.UUID(),
            sa.ForeignKey("promise_edits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "election_id",
            sa.UUID(),
            sa.ForeignKey("elections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promise_edit_election_links")),
        sa.UniqueConstraint(
            "edit_id",
            "election_id",
            name=op.f("uq__promise_edit_election_links__edit_id__election_id"),
        ),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("promise_edit_election_links")
    op.drop_table("promise_edits")
