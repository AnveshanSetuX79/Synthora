"""Add performance indexes

Revision ID: 014_add_performance_indexes
Revises: 013_add_notifications
Create Date: 2026-04-18 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for performance optimization."""
    
    # Index for notifications query (user_id + is_read)
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_id', 'is_read'],
        unique=False
    )
    
    # Unique index for businesses place_id (prevent duplicates)
    op.create_index(
        'idx_businesses_place_id',
        'businesses',
        ['place_id'],
        unique=True
    )
    
    # Index for business search (city + category)
    op.create_index(
        'idx_businesses_city_category',
        'businesses',
        ['city', 'category'],
        unique=False
    )
    
    # Index for lead contacts by freelancer
    op.create_index(
        'idx_lead_contacts_freelancer',
        'lead_contacts',
        ['freelancer_id'],
        unique=False
    )
    
    # Index for deals by status
    op.create_index(
        'idx_deals_status',
        'deals',
        ['status'],
        unique=False
    )
    
    # Index for messages by recipient
    op.create_index(
        'idx_messages_recipient',
        'messages',
        ['recipient_id'],
        unique=False
    )
    
    # Index for business insights by business_id
    op.create_index(
        'idx_business_insights_business',
        'business_insights',
        ['business_id'],
        unique=False
    )


def downgrade():
    """Remove indexes."""
    op.drop_index('idx_business_insights_business', table_name='business_insights')
    op.drop_index('idx_messages_recipient', table_name='messages')
    op.drop_index('idx_deals_status', table_name='deals')
    op.drop_index('idx_lead_contacts_freelancer', table_name='lead_contacts')
    op.drop_index('idx_businesses_city_category', table_name='businesses')
    op.drop_index('idx_businesses_place_id', table_name='businesses')
    op.drop_index('idx_notifications_user_read', table_name='notifications')
