"""fix interval time type

Revision ID: fix_interval_time_type
Revises: update_monitoring_interval_enum
Create Date: 2024-03-21 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_interval_time_type'
down_revision: Union[str, None] = 'update_monitoring_interval_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Primeiro converte a coluna para VARCHAR temporariamente
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR USING interval_time::VARCHAR")
    
    # Remove o tipo enum
    op.execute("DROP TYPE IF EXISTS monitoring_interval")
    
    # Converte os valores do enum para minutos
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
    
    # Altera a coluna para INTEGER
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE INTEGER USING interval_time::INTEGER")

def downgrade() -> None:
    # Primeiro converte para VARCHAR
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE VARCHAR USING interval_time::VARCHAR")
    
    # Cria o tipo enum
    op.execute(
        "CREATE TYPE monitoring_interval AS ENUM "
        "('10_minutes', '20_minutes', '30_minutes', '45_minutes', "
        "'1_hour', '2_hours', '5_hours', '12_hours', "
        "'1_day', '2_days', '1_week', '1_month')"
    )
    
    # Converte os valores de minutos para o enum
    op.execute("""
        UPDATE youtube_monitoring
        SET interval_time = CASE interval_time::INTEGER
            WHEN 10 THEN '10_minutes'
            WHEN 20 THEN '20_minutes'
            WHEN 30 THEN '30_minutes'
            WHEN 45 THEN '45_minutes'
            WHEN 60 THEN '1_hour'
            WHEN 120 THEN '2_hours'
            WHEN 300 THEN '5_hours'
            WHEN 720 THEN '12_hours'
            WHEN 1440 THEN '1_day'
            WHEN 2880 THEN '2_days'
            WHEN 10080 THEN '1_week'
            WHEN 43200 THEN '1_month'
            ELSE NULL
        END
    """)
    
    # Altera a coluna para usar o enum
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN interval_time TYPE monitoring_interval USING interval_time::monitoring_interval") 