"""Add business verification column

Revision ID: 009
Revises: 008
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add is_verified column to businesses table."""
    op.add_column('businesses', sa.Column('is_verified', sa.Boolean, default=False, nullable=False, server_default='false'))
    op.create_index('ix_businesses_is_verified', 'businesses', ['is_verified'])


def downgrade() -> None:
    """Remove is_verified column from businesses table."""
    op.drop_index('ix_businesses_is_verified', 'businesses')
    op.drop_column('businesses', 'is_verified')
