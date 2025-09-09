"""add agentequeimadura table and foreign key relationship

Revision ID: 24b1412cf938
Revises: 2084421f8f6c
Create Date: 2025-09-09 10:05:17.164064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '24b1412cf938'
down_revision: Union[str, Sequence[str], None] = '2084421f8f6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
