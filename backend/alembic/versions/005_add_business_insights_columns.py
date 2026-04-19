"""Add rating, review_count, has_website, website_url columns to business_insights

Revision ID: 005
Revises: 004
Create Date: 2026-04-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Add new columns to business_insights table."""
    
    # Add rating column
    op.add_column('business_insights', 
        sa.Column('rating', sa.Float(), nullable=True)
    )
    
    # Add review_count column
    op.add_column('business_insights', 
        sa.Column('review_count', sa.Integer(), nullable=True, server_default='0')
    )
    
    # Add has_website column
    op.add_column('business_insights', 
        sa.Column('has_website', sa.Boolean(), nullable=True, server_default='false')
    )
    op.create_index('ix_business_insights_has_website', 'business_insights', ['has_website'])
    
    # Add website_url column
    op.add_column('business_insights', 
        sa.Column('website_url', sa.String(500), nullable=True)
    )


def downgrade():
    """Remove columns from business_insights table."""
    
    op.drop_index('ix_business_insights_has_website', 'business_insights')
    op.drop_column('business_insights', 'website_url')
    op.drop_column('business_insights', 'has_website')
    op.drop_column('business_insights', 'review_count')
    op.drop_column('business_insights', 'rating')
