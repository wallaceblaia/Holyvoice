"""update_interval_time_column

Revision ID: update_interval_time_column
Revises: create_monitoring_playlist_table
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_interval_time_column'
down_revision: Union[str, None] = 'create_monitoring_playlist_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Altera a coluna interval_time para VARCHAR temporariamente
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR USING interval_time::VARCHAR")

    # Remove o tipo enum monitoring_interval
    op.execute("DROP TYPE monitoring_interval")

    # Atualiza os valores da coluna interval_time para minutos
    op.execute("""
        UPDATE youtube_monitoring
        SET interval_time = CASE interval_time
            WHEN '10_minutes' THEN '10'
            WHEN '20_minutes' THEN '20'
            WHEN '30_minutes' THEN '30'
            WHEN '45_minutes' THEN '45'
            WHEN '1_hour' THEN '60'
            WHEN '2_hours' THEN '120'
            WHEN '5_hours' THEN '300'
            WHEN '12_hours' THEN '720'
            WHEN '1_day' THEN '1440'
            WHEN '2_days' THEN '2880'
            WHEN '1_week' THEN '10080'
            WHEN '1_month' THEN '43200'
            ELSE NULL
        END
    """)

    # Altera a coluna interval_time para INTEGER
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE INTEGER USING interval_time::INTEGER")


def downgrade() -> None:
    # Altera a coluna interval_time para VARCHAR temporariamente
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR USING interval_time::VARCHAR")

    # Cria o tipo enum monitoring_interval
    op.execute("""
        CREATE TYPE monitoring_interval AS ENUM (
            '10_minutes',
            '20_minutes',
            '30_minutes',
            '45_minutes',
            '1_hour',
            '2_hours',
            '5_hours',
            '12_hours',
            '1_day',
            '2_days',
            '1_week',
            '1_month'
        )
    """)

    # Atualiza os valores da coluna interval_time para o formato anterior
    op.execute("""
        UPDATE youtube_monitoring
        SET interval_time = CASE interval_time
            WHEN '10' THEN '10_minutes'
            WHEN '20' THEN '20_minutes'
            WHEN '30' THEN '30_minutes'
            WHEN '45' THEN '45_minutes'
            WHEN '60' THEN '1_hour'
            WHEN '120' THEN '2_hours'
            WHEN '300' THEN '5_hours'
            WHEN '720' THEN '12_hours'
            WHEN '1440' THEN '1_day'
            WHEN '2880' THEN '2_days'
            WHEN '10080' THEN '1_week'
            WHEN '43200' THEN '1_month'
            ELSE NULL
        END
    """)

    # Altera a coluna interval_time para usar o tipo enum
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE monitoring_interval USING interval_time::monitoring_interval") 