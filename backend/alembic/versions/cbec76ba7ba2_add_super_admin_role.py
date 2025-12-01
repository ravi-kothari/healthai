"""add_super_admin_role

Revision ID: cbec76ba7ba2
Revises: 14948064f407
Create Date: 2025-11-30 22:20:25.721338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbec76ba7ba2'
down_revision = '14948064f407'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add SUPER_ADMIN to userrole enum
    # Note: ALTER TYPE ... ADD VALUE cannot be run inside a transaction block in some versions,
    # but Alembic usually handles this. If it fails, we might need to use commit().
    # However, 'IF NOT EXISTS' is only supported in Postgres 12+.
    # Since we are using postgres:15-alpine, it should be fine.
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPER_ADMIN'")


def downgrade() -> None:
    # Removing a value from an enum is not directly supported in Postgres
    pass
