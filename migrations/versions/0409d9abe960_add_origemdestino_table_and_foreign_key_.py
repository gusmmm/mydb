"""add origemdestino table and foreign key relationships

Revision ID: 0409d9abe960
Revises: 3262d9278c4d
Create Date: 2025-09-11 14:34:23.000022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0409d9abe960'
down_revision: Union[str, Sequence[str], None] = '3262d9278c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
