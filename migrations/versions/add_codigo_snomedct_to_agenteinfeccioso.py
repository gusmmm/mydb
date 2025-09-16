"""add codigo_snomedct column to agenteinfeccioso

Revision ID: add_codigo_snomedct
Revises: a61578a58409
Create Date: 2025-09-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_codigo_snomedct'
# Set down_revision to latest previous head to avoid multiple heads
down_revision: Union[str, None] = '87cf2f8181de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('agenteinfeccioso', sa.Column('codigo_snomedct', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('agenteinfeccioso', 'codigo_snomedct')
