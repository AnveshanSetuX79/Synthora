"""Rename metadata to failure_metadata in failure_logs

Revision ID: 012
Revises: 011
Create Date: 2026-04-18 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename metadata column to failure_metadata to avoid SQLAlchemy conflict."""
    # Check if the old column exists before renaming
    op.alter_column('failure_logs', 'metadata', new_column_name='failure_metadata')


def downgrade() -> None:
    """Rename failure_metadata back to metadata."""
    op.alter_column('failure_logs', 'failure_metadata', new_column_name='metadata')
