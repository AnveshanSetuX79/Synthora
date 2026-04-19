"""add analytics performance indexes

Revision ID: 017
Revises: 016
Create Date: 2026-04-19 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for analytics queries."""
    
    # Deal indexes - for freelancer ROI and funnel queries
    op.create_index(
        'idx_deal_freelancer_status_created',
        'deals',
        ['freelancer_id', 'status', 'created_at'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_deal_status_completed',
        'deals',
        ['status', 'completed_at'],
        postgresql_using='btree'
    )
    
    # Payment indexes - for revenue calculations
    op.create_index(
        'idx_payment_status_completed',
        'payments',
        ['status', 'completed_at'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_payment_deal_status',
        'payments',
        ['deal_id', 'status'],
        postgresql_using='btree'
    )
    
    # Lead contact indexes - for conversion funnel
    op.create_index(
        'idx_lead_contact_freelancer_created',
        'lead_contacts',
        ['freelancer_id', 'created_at'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_lead_contact_status_created',
        'lead_contacts',
        ['status', 'first_contact_at'],
        postgresql_using='btree'
    )
    
    # Analytics event indexes - for funnel tracking
    op.create_index(
        'idx_analytics_event_type_timestamp',
        'analytics_events',
        ['event_type', 'timestamp'],
        postgresql_using='btree'
    )
    
    op.create_index(
        'idx_analytics_event_user_timestamp',
        'analytics_events',
        ['user_id', 'timestamp'],
        postgresql_using='btree'
    )
    
    # Business owner indexes - for signup tracking
    op.create_index(
        'idx_business_owner_created',
        'business_owners',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Notification indexes - for unread count
    op.create_index(
        'idx_notification_user_read',
        'notifications',
        ['user_id', 'is_read'],
        postgresql_using='btree'
    )
    
    print("✅ Created 10 performance indexes for analytics queries")


def downgrade():
    """Remove performance indexes."""
    
    op.drop_index('idx_notification_user_read', table_name='notifications')
    op.drop_index('idx_business_owner_created', table_name='business_owners')
    op.drop_index('idx_analytics_event_user_timestamp', table_name='analytics_events')
    op.drop_index('idx_analytics_event_type_timestamp', table_name='analytics_events')
    op.drop_index('idx_lead_contact_status_created', table_name='lead_contacts')
    op.drop_index('idx_lead_contact_freelancer_created', table_name='lead_contacts')
    op.drop_index('idx_payment_deal_status', table_name='payments')
    op.drop_index('idx_payment_status_completed', table_name='payments')
    op.drop_index('idx_deal_status_completed', table_name='deals')
    op.drop_index('idx_deal_freelancer_status_created', table_name='deals')
    
    print("✅ Removed 10 performance indexes")
