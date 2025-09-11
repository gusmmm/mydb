"""change queimadura local_anatomico from integer to varchar

Revision ID: 86ac7b0fb500
Revises: 0648119e4f45
Create Date: 2025-09-11 14:57:59.599892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '86ac7b0fb500'
down_revision: Union[str, Sequence[str], None] = '0648119e4f45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table
    
    # Step 1: Create new table with correct column types
    op.create_table(
        'queimadura_new',
        sa.Column('internamento_id', sa.INTEGER(), nullable=False),
        sa.Column('local_anatomico', sa.VARCHAR(), nullable=True),
        sa.Column('grau_maximo', sa.VARCHAR(length=8), nullable=True),
        sa.Column('notas', sa.VARCHAR(), nullable=True),
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DATETIME(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('last_modified', sa.DATETIME(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['internamento_id'], ['internamento.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Step 2: Copy data from old table to new table
    # Since local_anatomico was INTEGER and we're changing to VARCHAR, we need to handle this
    op.execute(
        """
        INSERT INTO queimadura_new 
        (internamento_id, local_anatomico, grau_maximo, notas, id, created_at, last_modified)
        SELECT 
            internamento_id, 
            CAST(local_anatomico AS VARCHAR), 
            grau_maximo, 
            notas, 
            id, 
            created_at, 
            last_modified
        FROM queimadura
        """
    )
    
    # Step 3: Drop old table
    op.drop_table('queimadura')
    
    # Step 4: Rename new table
    op.rename_table('queimadura_new', 'queimadura')


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the process
    op.create_table(
        'queimadura_new',
        sa.Column('internamento_id', sa.INTEGER(), nullable=False),
        sa.Column('local_anatomico', sa.INTEGER(), nullable=True),
        sa.Column('grau_maximo', sa.VARCHAR(length=8), nullable=True),
        sa.Column('notas', sa.VARCHAR(), nullable=True),
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DATETIME(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('last_modified', sa.DATETIME(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['internamento_id'], ['internamento.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.execute(
        """
        INSERT INTO queimadura_new 
        (internamento_id, local_anatomico, grau_maximo, notas, id, created_at, last_modified)
        SELECT 
            internamento_id, 
            CAST(local_anatomico AS INTEGER), 
            grau_maximo, 
            notas, 
            id, 
            created_at, 
            last_modified
        FROM queimadura
        """
    )
    
    op.drop_table('queimadura')
    op.rename_table('queimadura_new', 'queimadura')
