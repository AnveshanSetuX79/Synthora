"""Add notifications and notification_preferences tables

Revision ID: 013
Revises: 012
Create Date: 2026-04-18 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create notifications and notification_preferences tables."""
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('type', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('link', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Create composite indexes
    op.create_index('ix_notifications_user_unread', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_notifications_user_created', 'notifications', ['user_id', 'created_at'])
    
    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, unique=True, index=True),
        
        # Email preferences
        sa.Column('email_new_message', sa.Boolean, default=True, nullable=False),
        sa.Column('email_milestone_submitted', sa.Boolean, default=True, nullable=False),
        sa.Column('email_milestone_approved', sa.Boolean, default=True, nullable=False),
        sa.Column('email_milestone_rejected', sa.Boolean, default=True, nullable=False),
        sa.Column('email_dispute_raised', sa.Boolean, default=True, nullable=False),
        sa.Column('email_payment_processed', sa.Boolean, default=True, nullable=False),
        
        # In-app preferences
        sa.Column('inapp_new_message', sa.Boolean, default=True, nullable=False),
        sa.Column('inapp_milestone_submitted', sa.Boolean, default=True, nullable=False),
        sa.Column('inapp_milestone_approved', sa.Boolean, default=True, nullable=False),
        sa.Column('inapp_milestone_rejected', sa.Boolean, default=True, nullable=False),
        sa.Column('inapp_dispute_raised', sa.Boolean, default=True, nullable=False),
        sa.Column('inapp_payment_processed', sa.Boolean, default=True, nullable=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    """Drop notifications and notification_preferences tables."""
    op.drop_index('ix_notifications_user_created', 'notifications')
    op.drop_index('ix_notifications_user_unread', 'notifications')
    op.drop_table('notifications')
    op.drop_table('notification_preferences')
