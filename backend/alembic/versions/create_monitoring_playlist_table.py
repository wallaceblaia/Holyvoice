"""create monitoring playlist table

Revision ID: create_monitoring_playlist_table
Revises: add_monitoring_video_columns
Create Date: 2024-02-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_monitoring_playlist_table'
down_revision: Union[str, None] = 'add_monitoring_video_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'monitoring_playlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitoring_id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['monitoring_id'], ['youtube_monitoring.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monitoring_playlist_id'), 'monitoring_playlist', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_monitoring_playlist_id'), table_name='monitoring_playlist')
    op.drop_table('monitoring_playlist')         