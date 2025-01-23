"""update monitoring status enum

Revision ID: update_monitoring_status_enum
Revises: create_monitoring_tables
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_monitoring_status_enum'
down_revision = 'create_monitoring_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update status values without using enum type
    op.execute("""
        UPDATE youtube_monitoring
        SET status = CASE status
            WHEN 'active' THEN 'active'
            WHEN 'paused' THEN 'paused'
            WHEN 'completed' THEN 'completed'
            WHEN 'error' THEN 'error'
            ELSE 'not_configured'
        END
    """)


def downgrade() -> None:
    # Update status values to original set
    op.execute("""
        UPDATE youtube_monitoring
        SET status = CASE status
            WHEN 'not_configured' THEN 'active'
            ELSE status
        END
    """)
