"""add is_processed column to documents

Revision ID: 001
Revises: 
Create Date: 2024-01-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_processed column to documents table
    op.add_column('documents', sa.Column('is_processed', sa.Boolean(), nullable=True))
    
    # Set default value for existing rows
    op.execute('UPDATE documents SET is_processed = false WHERE is_processed IS NULL')
    
    # Make column non-nullable
    op.alter_column('documents', 'is_processed', nullable=False, server_default=sa.false())


def downgrade() -> None:
    # Remove is_processed column
    op.drop_column('documents', 'is_processed')
