"""create provider tasks table

Revision ID: d6e7f8g9h0i1
Revises: c4d5e6f7g8h9
Create Date: 2024-11-20 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'd6e7f8g9h0i1'
down_revision = 'c4d5e6f7g8h9'
branch_labels = None
depends_on = None


def upgrade():
    # Create task_category enum
    task_category_enum = sa.Enum(
        'follow_up', 'lab_order', 'imaging_order', 'referral',
        'medication', 'phone_call', 'review', 'documentation', 'other',
        name='taskcategory'
    )
    task_category_enum.create(op.get_bind(), checkfirst=True)

    # Create task_priority enum
    task_priority_enum = sa.Enum(
        'low', 'medium', 'high', 'urgent',
        name='taskpriority'
    )
    task_priority_enum.create(op.get_bind(), checkfirst=True)

    # Create task_status enum
    task_status_enum = sa.Enum(
        'pending', 'in_progress', 'completed', 'cancelled',
        name='taskstatus'
    )
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Create provider_tasks table
    op.create_table(
        'provider_tasks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', task_category_enum, nullable=False),
        sa.Column('priority', task_priority_enum, nullable=False),
        sa.Column('status', task_status_enum, nullable=False),
        sa.Column('provider_id', sa.String(length=36), nullable=False),
        sa.Column('patient_id', sa.String(length=36), nullable=True),
        sa.Column('visit_id', sa.String(length=36), nullable=True),
        sa.Column('appointment_id', sa.String(length=36), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', JSON, nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_from_shortcut', sa.Boolean, default=False),
        sa.Column('shortcut_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create indexes
    op.create_index('ix_provider_tasks_id', 'provider_tasks', ['id'])
    op.create_index('ix_provider_tasks_provider_id', 'provider_tasks', ['provider_id'])
    op.create_index('ix_provider_tasks_patient_id', 'provider_tasks', ['patient_id'])
    op.create_index('ix_provider_tasks_visit_id', 'provider_tasks', ['visit_id'])
    op.create_index('ix_provider_tasks_appointment_id', 'provider_tasks', ['appointment_id'])

    # Create foreign keys
    op.create_foreign_key(
        'fk_provider_tasks_provider_id',
        'provider_tasks', 'users',
        ['provider_id'], ['id']
    )
    op.create_foreign_key(
        'fk_provider_tasks_patient_id',
        'provider_tasks', 'patients',
        ['patient_id'], ['id']
    )
    op.create_foreign_key(
        'fk_provider_tasks_visit_id',
        'provider_tasks', 'visits',
        ['visit_id'], ['id']
    )
    op.create_foreign_key(
        'fk_provider_tasks_appointment_id',
        'provider_tasks', 'appointments',
        ['appointment_id'], ['id']
    )


def downgrade():
    # Drop table
    op.drop_table('provider_tasks')

    # Drop enums
    sa.Enum(name='taskcategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)
