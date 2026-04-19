"""Add latitude and longitude to businesses

Revision ID: 007
Revises: 006
Create Date: 2024-01-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add latitude and longitude columns to businesses table."""
    op.add_column('businesses', 
        sa.Column('latitude', sa.DECIMAL(precision=10, scale=8), nullable=True)
    )
    op.add_column('businesses', 
        sa.Column('longitude', sa.DECIMAL(precision=11, scale=8), nullable=True)
    )
    
    # Create index for geospatial queries
    op.create_index('idx_businesses_coordinates', 'businesses', ['latitude', 'longitude'])


def downgrade():
    """Remove latitude and longitude columns from businesses table."""
    op.drop_index('idx_businesses_coordinates', table_name='businesses')
    op.drop_column('businesses', 'longitude')
    op.drop_column('businesses', 'latitude')
