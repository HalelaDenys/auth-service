"""first mg

Revision ID: 365f0dbd6ac6
Revises:
Create Date: 2026-01-20 15:45:47.714992

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "365f0dbd6ac6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.VARCHAR(length=50), nullable=False),
        sa.Column("last_name", sa.VARCHAR(length=50), nullable=True),
        sa.Column("email", sa.VARCHAR(length=100), nullable=False),
        sa.Column("phone_number", sa.VARCHAR(length=15), nullable=True),
        sa.Column("hashed_password", sa.VARCHAR(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="user_role"),
            server_default="user",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("phone_number", name=op.f("uq_users_phone_number")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
