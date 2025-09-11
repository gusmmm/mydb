"""add queimaduras table and foreign key relationship

Revision ID: 0648119e4f45
Revises: 0409d9abe960
Create Date: 2025-09-11 14:55:20.809337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0648119e4f45'
down_revision: Union[str, Sequence[str], None] = '0409d9abe960'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
