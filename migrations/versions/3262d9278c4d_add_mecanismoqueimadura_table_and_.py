"""add mecanismoqueimadura table and foreign key relationship

Revision ID: 3262d9278c4d
Revises: 24b1412cf938
Create Date: 2025-09-11 14:12:43.342388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3262d9278c4d'
down_revision: Union[str, Sequence[str], None] = '24b1412cf938'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
