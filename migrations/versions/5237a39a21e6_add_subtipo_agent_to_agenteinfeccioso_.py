"""add subtipo_agent to agenteinfeccioso table

Revision ID: 5237a39a21e6
Revises: add_codigo_snomedct
Create Date: 2025-09-17 15:00:37.776400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5237a39a21e6'
down_revision: Union[str, Sequence[str], None] = 'add_codigo_snomedct'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add subtipo_agent column to agenteinfeccioso table
    op.add_column('agenteinfeccioso', sa.Column('subtipo_agent', sa.VARCHAR(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove subtipo_agent column from agenteinfeccioso table
    op.drop_column('agenteinfeccioso', 'subtipo_agent')
