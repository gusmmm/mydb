"""add procedimento and internamentoprocedimento tables

Revision ID: a61578a58409
Revises: e49203047170
Create Date: 2025-09-15 20:09:59.182051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a61578a58409'
down_revision: Union[str, Sequence[str], None] = 'e49203047170'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create procedimento table
    op.create_table(
        'procedimento',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('nome_procedimento', sa.String(), nullable=False),
        sa.Column('tipo_procedimento', sa.String(), nullable=True),
    )
    
    # Create internamentoprocedimento table
    op.create_table(
        'internamentoprocedimento',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('internamento_id', sa.Integer(), nullable=False),
        sa.Column('procedimento', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['internamento_id'], ['internamento.id'], name=None
        ),
        sa.ForeignKeyConstraint(['procedimento'], ['procedimento.id'], name=None),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('internamentoprocedimento')
    op.drop_table('procedimento')
