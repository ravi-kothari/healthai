"""add visits and transcripts tables

Revision ID: a1b2c3d4e5f6
Revises: 4e807a69e5a7
Create Date: 2025-11-02 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '4e807a69e5a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create visits table
    op.create_table(
        'visits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visit_type', sa.Enum('INITIAL', 'FOLLOW_UP', 'URGENT', 'ROUTINE', 'TELEHEALTH', 'IN_PERSON', name='visittype'), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW', name='visitstatus'), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('reason_for_visit', sa.Text(), nullable=True),
        sa.Column('subjective', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('assessment', sa.Text(), nullable=True),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('vitals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('diagnoses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('medications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('procedures', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('fhir_encounter_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visits_id'), 'visits', ['id'], unique=False)
    op.create_index(op.f('ix_visits_patient_id'), 'visits', ['patient_id'], unique=False)
    op.create_index(op.f('ix_visits_provider_id'), 'visits', ['provider_id'], unique=False)

    # Create transcripts table
    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('audio_file_url', sa.String(length=500), nullable=True),
        sa.Column('audio_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('audio_format', sa.String(length=50), nullable=True),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='transcriptionstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['visit_id'], ['visits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcripts_id'), 'transcripts', ['id'], unique=False)
    op.create_index(op.f('ix_transcripts_visit_id'), 'transcripts', ['visit_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_transcripts_visit_id'), table_name='transcripts')
    op.drop_index(op.f('ix_transcripts_id'), table_name='transcripts')
    op.drop_table('transcripts')

    op.drop_index(op.f('ix_visits_provider_id'), table_name='visits')
    op.drop_index(op.f('ix_visits_patient_id'), table_name='visits')
    op.drop_index(op.f('ix_visits_id'), table_name='visits')
    op.drop_table('visits')

    op.execute('DROP TYPE IF EXISTS transcriptionstatus')
    op.execute('DROP TYPE IF EXISTS visitstatus')
    op.execute('DROP TYPE IF EXISTS visittype')
