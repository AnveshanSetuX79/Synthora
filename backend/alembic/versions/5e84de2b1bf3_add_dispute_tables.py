"""add_dispute_tables

Revision ID: 5e84de2b1bf3
Revises: acf9bc5fd885
Create Date: 2026-04-18 15:07:27.963506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e84de2b1bf3'
down_revision = 'acf9bc5fd885'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create disputes table
    op.create_table(
        'disputes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('deal_id', sa.String(36), sa.ForeignKey('deals.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('raised_by', sa.String(36), nullable=False),
        sa.Column('raised_by_role', sa.String(50), nullable=False),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(50), default='open', nullable=False),
        sa.Column('resolution_type', sa.String(50), nullable=True),
        sa.Column('resolution_amount', sa.Integer, nullable=True),
        sa.Column('resolution_notes', sa.Text, nullable=True),
        sa.Column('resolved_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('self_resolution_deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_disputes_deal_id', 'disputes', ['deal_id'])
    op.create_index('ix_disputes_status', 'disputes', ['status'])
    op.create_index('ix_disputes_created_at', 'disputes', ['created_at'])
    
    # Create dispute_messages table
    op.create_table(
        'dispute_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dispute_id', sa.String(36), sa.ForeignKey('disputes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('sender_role', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('is_system_message', sa.String(10), default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_dispute_messages_dispute_id', 'dispute_messages', ['dispute_id'])
    op.create_index('ix_dispute_messages_created_at', 'dispute_messages', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_dispute_messages_created_at', 'dispute_messages')
    op.drop_index('ix_dispute_messages_dispute_id', 'dispute_messages')
    op.drop_index('ix_disputes_created_at', 'disputes')
    op.drop_index('ix_disputes_status', 'disputes')
    op.drop_index('ix_disputes_deal_id', 'disputes')
    
    # Drop tables
    op.drop_table('dispute_messages')
    op.drop_table('disputes')
