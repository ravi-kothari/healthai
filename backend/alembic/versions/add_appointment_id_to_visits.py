"""add appointment_id to visits

Revision ID: c4d5e6f7g8h9
Revises: b2c3d4e5f6g7
Create Date: 2024-11-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4d5e6f7g8h9'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Add appointment_id column to visits table
    op.add_column('visits', sa.Column('appointment_id', sa.String(length=36), nullable=True))
    op.create_index('ix_visits_appointment_id', 'visits', ['appointment_id'])
    op.create_foreign_key('fk_visits_appointment_id', 'visits', 'appointments', ['appointment_id'], ['id'])


def downgrade():
    # Remove appointment_id column from visits table
    op.drop_constraint('fk_visits_appointment_id', 'visits', type_='foreignkey')
    op.drop_index('ix_visits_appointment_id', 'visits')
    op.drop_column('visits', 'appointment_id')
