"""initial_schema

Revision ID: 20260521_000001
Revises:
Create Date: 2026-05-21 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260521_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=150), nullable=False),
        sa.Column(
            "role",
            sa.Enum("registered", "moderator", "admin", name="user_role"),
            nullable=False,
        ),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("account_age_days", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__users")),
        sa.UniqueConstraint("email", name=op.f("uq__users__email")),
    )

    # 2. parties
    op.create_table(
        "parties",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name_hy", sa.String(length=200), nullable=False),
        sa.Column("short_name_hy", sa.String(length=50), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__parties")),
    )

    # 3. politicians (FK to parties, users)
    op.create_table(
        "politicians",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name_hy", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("position", sa.String(length=200), nullable=True),
        sa.Column(
            "level",
            sa.Enum("national", "local", "party", name="politician_level"),
            nullable=False,
        ),
        sa.Column("party_id", sa.UUID(), nullable=True),
        sa.Column("bio_hy", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk__politicians__created_by__users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["party_id"],
            ["parties.id"],
            name=op.f("fk__politicians__party_id__parties"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__politicians")),
        sa.UniqueConstraint("slug", name=op.f("uq__politicians__slug")),
    )

    # 4. politician_party_memberships (FK to politicians, parties)
    op.create_table(
        "politician_party_memberships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("politician_id", sa.UUID(), nullable=False),
        sa.Column("party_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["party_id"],
            ["parties.id"],
            name=op.f("fk__politician_party_memberships__party_id__parties"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politicians.id"],
            name=op.f("fk__politician_party_memberships__politician_id__politicians"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__politician_party_memberships")),
    )

    # 5. elections (FK to users)
    op.create_table(
        "elections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name_hy", sa.String(length=300), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("election_date", sa.Date(), nullable=False),
        sa.Column(
            "level",
            sa.Enum("national", "local", "referendum", name="election_level"),
            nullable=False,
        ),
        sa.Column("description_hy", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk__elections__created_by__users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__elections")),
        sa.UniqueConstraint("slug", name=op.f("uq__elections__slug")),
    )

    # 6. promises (FK to politicians, users)
    op.create_table(
        "promises",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title_hy", sa.String(length=500), nullable=False),
        sa.Column("quote_hy", sa.Text(), nullable=False),
        sa.Column("description_hy", sa.Text(), nullable=True),
        sa.Column("politician_id", sa.UUID(), nullable=False),
        sa.Column("made_date", sa.Date(), nullable=True),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("archived_url", sa.Text(), nullable=True),
        sa.Column("quote_excerpt", sa.Text(), nullable=True),
        sa.Column("slug", sa.String(length=300), nullable=False),
        sa.Column(
            "moderation_status",
            sa.Enum("pending", "approved", "rejected", name="moderation_status"),
            nullable=False,
        ),
        sa.Column(
            "resolved_status",
            sa.Enum("not_rated", "kept", "broken", "in_progress", "stalled", name="resolved_status"),
            nullable=False,
        ),
        sa.Column("is_seed", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk__promises__created_by__users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politicians.id"],
            name=op.f("fk__promises__politician_id__politicians"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promises")),
        sa.UniqueConstraint("slug", name=op.f("uq__promises__slug")),
    )

    # 7. promise_election_links (FK to promises, elections)
    op.create_table(
        "promise_election_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("promise_id", sa.UUID(), nullable=False),
        sa.Column("election_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["election_id"],
            ["elections.id"],
            name=op.f("fk__promise_election_links__election_id__elections"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["promise_id"],
            ["promises.id"],
            name=op.f("fk__promise_election_links__promise_id__promises"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promise_election_links")),
        sa.UniqueConstraint(
            "promise_id",
            "election_id",
            name="uq__promise_election_links__promise_id__election_id",
        ),
    )

    # 8. evidence (FK to promises, users)
    op.create_table(
        "evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("promise_id", sa.UUID(), nullable=False),
        sa.Column("submitted_by", sa.UUID(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("archived_url", sa.Text(), nullable=True),
        sa.Column("quote_excerpt", sa.Text(), nullable=True),
        sa.Column("title_hy", sa.String(length=300), nullable=True),
        sa.Column("description_hy", sa.Text(), nullable=True),
        sa.Column(
            "evidence_type",
            sa.Enum("supports_kept", "supports_broken", "neutral", name="evidence_type"),
            nullable=False,
        ),
        sa.Column(
            "moderation_status",
            sa.Enum("pending", "approved", "rejected", name="moderation_status"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["promise_id"],
            ["promises.id"],
            name=op.f("fk__evidence__promise_id__promises"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["users.id"],
            name=op.f("fk__evidence__submitted_by__users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__evidence")),
    )

    # 9. votes (FK to promises, users)
    op.create_table(
        "votes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("promise_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "status_voted",
            sa.Enum("kept", "broken", "in_progress", "stalled", "not_rated", name="vote_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["promise_id"],
            ["promises.id"],
            name=op.f("fk__votes__promise_id__promises"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk__votes__user_id__users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__votes")),
        sa.UniqueConstraint("promise_id", "user_id", name="uq__votes__promise_id__user_id"),
    )

    # 10. vote_history (FK to promises, users)
    op.create_table(
        "vote_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("promise_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "status_voted",
            sa.Enum("kept", "broken", "in_progress", "stalled", "not_rated", name="vote_status"),
            nullable=False,
        ),
        sa.Column("voted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "previous_status",
            sa.Enum("kept", "broken", "in_progress", "stalled", "not_rated", name="vote_status"),
            nullable=True,
        ),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["promise_id"],
            ["promises.id"],
            name=op.f("fk__vote_history__promise_id__promises"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk__vote_history__user_id__users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__vote_history")),
    )

    # 11. stats_cache (FK to politicians)
    op.create_table(
        "stats_cache",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("politician_id", sa.UUID(), nullable=False),
        sa.Column("total_promises", sa.Integer(), nullable=False),
        sa.Column("kept_count", sa.Integer(), nullable=False),
        sa.Column("broken_count", sa.Integer(), nullable=False),
        sa.Column("in_progress_count", sa.Integer(), nullable=False),
        sa.Column("stalled_count", sa.Integer(), nullable=False),
        sa.Column("not_rated_count", sa.Integer(), nullable=False),
        sa.Column("fulfillment_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["politician_id"],
            ["politicians.id"],
            name=op.f("fk__stats_cache__politician_id__politicians"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__stats_cache")),
        sa.UniqueConstraint("politician_id", name="uq__stats_cache__politician_id"),
    )

    # 12. app_settings (no FKs)
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("key", name=op.f("pk__app_settings")),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_table("stats_cache")
    op.drop_table("vote_history")
    op.drop_table("votes")
    op.drop_table("evidence")
    op.drop_table("promise_election_links")
    op.drop_table("promises")
    op.drop_table("elections")
    op.drop_table("politician_party_memberships")
    op.drop_table("politicians")
    op.drop_table("parties")
    op.drop_table("users")
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS vote_status")
    op.execute("DROP TYPE IF EXISTS evidence_type")
    op.execute("DROP TYPE IF EXISTS resolved_status")
    op.execute("DROP TYPE IF EXISTS moderation_status")
    op.execute("DROP TYPE IF EXISTS election_level")
    op.execute("DROP TYPE IF EXISTS politician_level")
    op.execute("DROP TYPE IF EXISTS user_role")
