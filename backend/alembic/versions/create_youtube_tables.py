"""create youtube tables

Revision ID: create_youtube_tables
Revises: 
Create Date: 2024-03-18 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'create_youtube_tables'
down_revision: Union[str, None] = 'create_user_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Cria a tabela youtube_channel
    op.create_table(
        'youtube_channel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_url', sa.String(), nullable=False),
        sa.Column('youtube_id', sa.String(), nullable=False),
        sa.Column('channel_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('banner_image', sa.String(), nullable=True),
        sa.Column('avatar_image', sa.String(), nullable=True),
        sa.Column('subscriber_count', sa.Integer(), nullable=True),
        sa.Column('video_count', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youtube_channel_id'), 'youtube_channel', ['id'], unique=False)
    op.create_index(op.f('ix_youtube_channel_youtube_id'), 'youtube_channel', ['youtube_id'], unique=False)

    # Cria a tabela youtube_channel_access
    op.create_table(
        'youtube_channel_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('can_view', sa.Boolean(), nullable=True, default=False),
        sa.Column('can_edit', sa.Boolean(), nullable=True, default=False),
        sa.Column('can_delete', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['youtube_channel.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youtube_channel_access_id'), 'youtube_channel_access', ['id'], unique=False)

    # Cria a tabela youtube_playlist
    op.create_table(
        'youtube_playlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('video_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['youtube_channel.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youtube_playlist_id'), 'youtube_playlist', ['id'], unique=False)
    op.create_index(op.f('ix_youtube_playlist_playlist_id'), 'youtube_playlist', ['playlist_id'], unique=False)

    # Cria a tabela youtube_video
    op.create_table(
        'youtube_video',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.Integer(), nullable=True),
        sa.Column('video_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('is_live', sa.Boolean(), nullable=True, default=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('video_quality', sa.Text(), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('category', sa.Text(), nullable=True),
        sa.Column('original_language', sa.Text(), nullable=True),
        sa.Column('like_count', sa.Integer(), nullable=True),
        sa.Column('comment_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['youtube_channel.id'], ),
        sa.ForeignKeyConstraint(['playlist_id'], ['youtube_playlist.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youtube_video_id'), 'youtube_video', ['id'], unique=False)
    op.create_index(op.f('ix_youtube_video_video_id'), 'youtube_video', ['video_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_youtube_video_video_id'), table_name='youtube_video')
    op.drop_index(op.f('ix_youtube_video_id'), table_name='youtube_video')
    op.drop_table('youtube_video')
    
    op.drop_index(op.f('ix_youtube_playlist_playlist_id'), table_name='youtube_playlist')
    op.drop_index(op.f('ix_youtube_playlist_id'), table_name='youtube_playlist')
    op.drop_table('youtube_playlist')
    
    op.drop_index(op.f('ix_youtube_channel_access_id'), table_name='youtube_channel_access')
    op.drop_table('youtube_channel_access')
    
    op.drop_index(op.f('ix_youtube_channel_youtube_id'), table_name='youtube_channel')
    op.drop_index(op.f('ix_youtube_channel_id'), table_name='youtube_channel')
    op.drop_table('youtube_channel')
