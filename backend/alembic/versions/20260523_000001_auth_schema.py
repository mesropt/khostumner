"""auth_schema

Revision ID: 20260523_000001
Revises: 20260522_000001
Create Date: 2026-05-23 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260523_000001"
down_revision: Union[str, None] = "20260522_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename password_hash -> hashed_password (FastAPI-Users expects this column name)
    op.alter_column("users", "password_hash", new_column_name="hashed_password")

    # 2. Rename email_verified -> is_verified (FastAPI-Users expects this column name)
    op.alter_column("users", "email_verified", new_column_name="is_verified")

    # 3. Add is_superuser column (required by FastAPI-Users; missing from Phase 1 schema)
    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
    )

    # 4. Create oauth_accounts table for Google/Facebook OAuth integration
    #    NOTE: access_token is String(4096) — Google RS256 tokens exceed 1024 chars (RESEARCH.md Pitfall 3)
    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("oauth_name", sa.String(length=100), nullable=False),
        sa.Column("access_token", sa.String(length=4096), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("refresh_token", sa.String(length=4096), nullable=True),
        sa.Column("account_id", sa.String(length=320), nullable=False),
        sa.Column("account_email", sa.String(length=320), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk__oauth_accounts__user_id__users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__oauth_accounts")),
    )
    op.create_index(
        op.f("ix__oauth_accounts__oauth_name"), "oauth_accounts", ["oauth_name"]
    )
    op.create_index(
        op.f("ix__oauth_accounts__account_id"), "oauth_accounts", ["account_id"]
    )
    op.create_index(
        op.f("ix__oauth_accounts__account_email"), "oauth_accounts", ["account_email"]
    )


def downgrade() -> None:
    # Reverse in reverse order
    op.drop_index(op.f("ix__oauth_accounts__account_email"), table_name="oauth_accounts")
    op.drop_index(op.f("ix__oauth_accounts__account_id"), table_name="oauth_accounts")
    op.drop_index(op.f("ix__oauth_accounts__oauth_name"), table_name="oauth_accounts")
    op.drop_table("oauth_accounts")
    op.drop_column("users", "is_superuser")
    op.alter_column("users", "is_verified", new_column_name="email_verified")
    op.alter_column("users", "hashed_password", new_column_name="password_hash")
