"""update monitoring status enum

Revision ID: update_monitoring_status_enum
Revises: create_monitoring_tables
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_monitoring_status_enum'
down_revision: Union[str, None] = 'create_monitoring_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Primeiro remove a restrição do enum antigo
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN status TYPE VARCHAR")
    
    # Recria o enum com os valores corretos
    op.execute("DROP TYPE IF EXISTS monitoring_status")
    op.execute(
        "CREATE TYPE monitoring_status AS ENUM "
        "('not_configured', 'active', 'paused', 'completed', 'error')"
    )
    
    # Atualiza a coluna para usar o novo enum
    op.execute(
        "ALTER TABLE youtube_monitoring "
        "ALTER COLUMN status TYPE monitoring_status "
        "USING status::monitoring_status"
    )


def downgrade() -> None:
    # Remove a restrição do enum novo
    op.execute("ALTER TABLE youtube_monitoring ALTER COLUMN status TYPE VARCHAR")
    
    # Recria o enum com os valores antigos
    op.execute("DROP TYPE IF EXISTS monitoring_status")
    op.execute(
        "CREATE TYPE monitoring_status AS ENUM "
        "('active', 'paused', 'completed', 'error')"
    )
    
    # Atualiza a coluna para usar o enum antigo
    op.execute(
        "ALTER TABLE youtube_monitoring "
        "ALTER COLUMN status TYPE monitoring_status "
        "USING status::monitoring_status"
    ) 