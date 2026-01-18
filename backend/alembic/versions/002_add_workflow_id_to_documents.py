"""add workflow_id to documents

Revision ID: 002
Revises: 001
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add workflow_id column to documents table
    op.add_column('documents', sa.Column('workflow_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_documents_workflow_id', 'documents', 'workflows', ['workflow_id'], ['id'])


def downgrade():
    # Remove foreign key and column
    op.drop_constraint('fk_documents_workflow_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'workflow_id')
