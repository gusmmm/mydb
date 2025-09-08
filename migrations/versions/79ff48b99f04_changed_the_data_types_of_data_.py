"""changed the data types of data_nascimento, data_entrada and data_saida to date

Revision ID: 79ff48b99f04
Revises: 4685a871eef9
Create Date: 2025-09-07 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79ff48b99f04'
down_revision: Union[str, Sequence[str], None] = '4685a871eef9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - this migration was already applied manually."""
    # This migration was intended to change string dates to date types
    # but the schema was already created with date types, so no changes needed
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No changes to revert
    pass