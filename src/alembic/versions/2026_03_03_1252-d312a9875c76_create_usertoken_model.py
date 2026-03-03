"""create UserToken model

Revision ID: d312a9875c76
Revises: f76402fe2c7f
Create Date: 2026-03-03 12:52:43.044242

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d312a9875c76"
down_revision: Union[str, Sequence[str], None] = "f76402fe2c7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_tokens",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lookup_hash", sa.String(), nullable=False),
        sa.Column("hashed_token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "token_type",
            sa.Enum(
                "reset_password",
                "verify_email",
                name="tokentypeenum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_tokens")),
    )
    op.create_index(
        op.f("ix_user_tokens_lookup_hash"), "user_tokens", ["lookup_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_tokens_lookup_hash"), table_name="user_tokens")
    op.drop_table("user_tokens")
