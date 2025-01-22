"""update monitoring interval enum

Revision ID: update_monitoring_interval_enum
Revises: update_monitoring_status_enum
Create Date: 2024-03-19 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_monitoring_interval_enum'
down_revision: Union[str, None] = 'update_monitoring_status_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Primeiro remove a restrição do enum antigo
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR")
    
    # Recria o enum com os valores corretos
    op.execute("DROP TYPE IF EXISTS monitoring_interval")
    op.execute(
        "CREATE TYPE monitoring_interval AS ENUM "
        "('10_minutes', '20_minutes', '30_minutes', '45_minutes', "
        "'1_hour', '2_hours', '5_hours', '12_hours', "
        "'1_day', '2_days', '1_week', '1_month')"
    )
    
    # Atualiza a coluna para usar o novo enum
    op.execute(
        "ALTER TABLE youtube_monitoring "
        "ALTER COLUMN interval_time TYPE monitoring_interval "
        "USING interval_time::monitoring_interval"
    )


def downgrade() -> None:
    # Remove a restrição do enum novo
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR")
    
    # Recria o enum com os valores antigos
    op.execute("DROP TYPE IF EXISTS monitoring_interval")
    op.execute(
        "CREATE TYPE monitoring_interval AS ENUM "
        "('MIN_10', 'MIN_20', 'MIN_30', 'MIN_45', "
        "'HOUR_1', 'HOUR_2', 'HOUR_5', 'HOUR_12', "
        "'DAY_1', 'DAY_2', 'WEEK_1', 'MONTH_1')"
    )
    
    # Atualiza a coluna para usar o enum antigo
    op.execute(
        "ALTER TABLE youtube_monitoring "
        "ALTER COLUMN interval_time TYPE monitoring_interval "
        "USING interval_time::monitoring_interval"
    ) 