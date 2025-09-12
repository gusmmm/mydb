"""add infection-related tables: agenteinfeccioso, tipoinfecao, and infecao

Revision ID: 89b0de97ba33
Revises: b8c76b2c5c11
Create Date: 2025-09-12 08:33:08.002931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '89b0de97ba33'
down_revision: Union[str, Sequence[str], None] = 'b8c76b2c5c11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
