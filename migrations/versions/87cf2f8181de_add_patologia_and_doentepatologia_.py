"""add patologia and doentepatologia tables with foreign key relationships

Revision ID: 87cf2f8181de
Revises: f663e0942c73
Create Date: 2025-09-15 20:49:51.048415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '87cf2f8181de'
down_revision: Union[str, Sequence[str], None] = 'f663e0942c73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create patologia table
    op.create_table(
        'patologia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome_patologia', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('classe_patologia', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('codigo', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_modified', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create doentepatologia table
    op.create_table(
        'doentepatologia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doente_id', sa.Integer(), nullable=False),
        sa.Column('patologia', sa.Integer(), nullable=True),
        sa.Column('nota', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_modified', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['doente_id'], ['doente.id'], ),
        sa.ForeignKeyConstraint(['patologia'], ['patologia.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('doentepatologia')
    op.drop_table('patologia')
