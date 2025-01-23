"""add monitoring video columns

Revision ID: add_monitoring_video_columns
Revises: update_monitoring_status_enum
Create Date: 2024-03-21 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_monitoring_video_columns'
down_revision: Union[str, None] = 'update_monitoring_status_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Adiciona novas colunas na tabela monitoring_video
    op.add_column('monitoring_video', sa.Column('download_progress', sa.Float(), nullable=True))
    op.add_column('monitoring_video', sa.Column('download_started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('monitoring_video', sa.Column('download_completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('monitoring_video', sa.Column('project_path', sa.Text(), nullable=True))
    op.add_column('monitoring_video', sa.Column('source_path', sa.Text(), nullable=True))

def downgrade() -> None:
    # Remove as colunas adicionadas
    op.drop_column('monitoring_video', 'source_path')
    op.drop_column('monitoring_video', 'project_path')
    op.drop_column('monitoring_video', 'download_completed_at')
    op.drop_column('monitoring_video', 'download_started_at')
    op.drop_column('monitoring_video', 'download_progress')
