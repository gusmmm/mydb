"""add traumatipo and trauma tables with foreign key relationships

Revision ID: f20f382d77a5
Revises: cf45754f53ea
Create Date: 2025-09-12 07:54:45.419817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f20f382d77a5'
down_revision: Union[str, Sequence[str], None] = 'cf45754f53ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
