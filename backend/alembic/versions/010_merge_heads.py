"""Merge migration heads

Revision ID: 010
Revises: 009, dfd8191d5b81
Create Date: 2024-01-20 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010'
down_revision = ('009', 'dfd8191d5b81')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge heads - no changes needed."""
    pass


def downgrade() -> None:
    """Merge heads - no changes needed."""
    pass
