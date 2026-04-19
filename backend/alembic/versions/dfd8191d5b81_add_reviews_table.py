"""add_reviews_table

Revision ID: dfd8191d5b81
Revises: 5e84de2b1bf3
Create Date: 2026-04-18 15:22:21.584811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfd8191d5b81'
down_revision = '5e84de2b1bf3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('deal_id', sa.String(36), sa.ForeignKey('deals.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('freelancer_id', sa.String(36), sa.ForeignKey('freelancers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('business_owner_id', sa.String(36), sa.ForeignKey('business_owners.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('review_text', sa.Text, nullable=False),
        sa.Column('response_text', sa.Text, nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.CheckConstraint('LENGTH(review_text) >= 20', name='check_review_min_length')
    )
    
    # Create indexes
    op.create_index('ix_reviews_deal_id', 'reviews', ['deal_id'])
    op.create_index('ix_reviews_freelancer_id', 'reviews', ['freelancer_id'])
    op.create_index('ix_reviews_business_owner_id', 'reviews', ['business_owner_id'])
    op.create_index('ix_reviews_created_at', 'reviews', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_reviews_created_at', 'reviews')
    op.drop_index('ix_reviews_business_owner_id', 'reviews')
    op.drop_index('ix_reviews_freelancer_id', 'reviews')
    op.drop_index('ix_reviews_deal_id', 'reviews')
    
    # Drop table
    op.drop_table('reviews')
