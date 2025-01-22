"""create monitoring tables

Revision ID: create_monitoring_tables
Revises: create_youtube_tables
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_monitoring_tables'
down_revision = 'create_youtube_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Cria o enum para intervalos de monitoramento
    op.execute("""
        CREATE TYPE monitoring_interval AS ENUM (
            '10_minutes', '20_minutes', '30_minutes', '45_minutes',
            '1_hour', '2_hours', '5_hours', '12_hours',
            '1_day', '2_days', '1_week', '1_month'
        )
    """)

    # Cria o enum para status do monitoramento
    op.execute("""
        CREATE TYPE monitoring_status AS ENUM (
            'active', 'paused', 'completed', 'error'
        )
    """)

    # Cria o enum para status do processamento de vídeo
    op.execute("""
        CREATE TYPE video_processing_status AS ENUM (
            'pending', 'processing', 'completed', 'error', 'skipped'
        )
    """)

    # Cria a tabela de monitoramento
    op.create_table(
        'youtube_monitoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_continuous', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('interval_time', sa.Enum('monitoring_interval', native_enum=False), nullable=True),
        sa.Column('status', sa.Enum('monitoring_status', native_enum=False), nullable=False, server_default='active'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_check_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_check_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['youtube_channel.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youtube_monitoring_id'), 'youtube_monitoring', ['id'], unique=False)

    # Cria a tabela de vídeos monitorados
    op.create_table(
        'monitoring_video',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitoring_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('video_processing_status', native_enum=False), nullable=False, server_default='pending'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['monitoring_id'], ['youtube_monitoring.id'], ),
        sa.ForeignKeyConstraint(['video_id'], ['youtube_video.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monitoring_video_id'), 'monitoring_video', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_monitoring_video_id'), table_name='monitoring_video')
    op.drop_table('monitoring_video')
    op.drop_index(op.f('ix_youtube_monitoring_id'), table_name='youtube_monitoring')
    op.drop_table('youtube_monitoring')
    op.execute('DROP TYPE video_processing_status')
    op.execute('DROP TYPE monitoring_status')
    op.execute('DROP TYPE monitoring_interval') 