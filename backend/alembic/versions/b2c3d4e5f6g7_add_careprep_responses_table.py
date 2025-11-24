"""add careprep responses table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create careprep_responses table
    op.create_table(
        'careprep_responses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('appointment_id', sa.String(length=36), nullable=False),
        sa.Column('patient_id', sa.String(length=36), nullable=False),

        # Medical History
        sa.Column('medical_history_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('medical_history_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('medical_history_updated_at', sa.DateTime(), nullable=True),

        # Symptom Checker
        sa.Column('symptom_checker_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('symptom_checker_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('symptom_checker_updated_at', sa.DateTime(), nullable=True),

        # Overall completion
        sa.Column('all_tasks_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Primary key
        sa.PrimaryKeyConstraint('id'),

        # Foreign keys
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    )

    # Create indexes for better query performance
    op.create_index('ix_careprep_responses_appointment_id', 'careprep_responses', ['appointment_id'])
    op.create_index('ix_careprep_responses_patient_id', 'careprep_responses', ['patient_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_careprep_responses_patient_id', table_name='careprep_responses')
    op.drop_index('ix_careprep_responses_appointment_id', table_name='careprep_responses')

    # Drop table
    op.drop_table('careprep_responses')
