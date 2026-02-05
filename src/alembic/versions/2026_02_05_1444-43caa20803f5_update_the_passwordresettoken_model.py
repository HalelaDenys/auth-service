"""update the PasswordResetToken model

Revision ID: 43caa20803f5
Revises: 86420b6a78da
Create Date: 2026-02-05 14:44:34.323543

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "43caa20803f5"
down_revision: Union[str, Sequence[str], None] = "86420b6a78da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "password_reset_tokens", sa.Column("lookup_hash", sa.String(), nullable=False)
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_hashed_token"),
        table_name="password_reset_tokens",
    )
    op.create_index(
        op.f("ix_password_reset_tokens_lookup_hash"),
        "password_reset_tokens",
        ["lookup_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_password_reset_tokens_lookup_hash"), table_name="password_reset_tokens"
    )
    op.create_index(
        op.f("ix_password_reset_tokens_hashed_token"),
        "password_reset_tokens",
        ["hashed_token"],
        unique=True,
    )
    op.drop_column("password_reset_tokens", "lookup_hash")
