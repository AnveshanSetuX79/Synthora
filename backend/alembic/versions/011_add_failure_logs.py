"""Add failure logs table

Revision ID: 011
Revises: 010
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create failure_logs table for retry logic."""
    
    # Create failure_logs table using String for status instead of enum
    op.create_table(
        'failure_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('service', sa.String(50), nullable=False, index=True),  # 'sms', 'email', 'payment'
        sa.Column('operation', sa.String(100), nullable=False),
        sa.Column('target', sa.String(255), nullable=False),  # phone/email/payment_id
        sa.Column('attempt_number', sa.Integer, nullable=False, default=0),
        sa.Column('max_attempts', sa.Integer, nullable=False, default=3),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('failure_metadata', postgresql.JSON, nullable=True),  # Renamed from 'metadata'
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        sa.Column('admin_notified', sa.Boolean, default=False, nullable=False),
        sa.Column('fallback_attempted', sa.Boolean, default=False, nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_failure_logs_service', 'failure_logs', ['service'])
    op.create_index('ix_failure_logs_status', 'failure_logs', ['status'])
    op.create_index('ix_failure_logs_next_retry', 'failure_logs', ['next_retry_at'])
    op.create_index('ix_failure_logs_created_at', 'failure_logs', ['created_at'])


def downgrade() -> None:
    """Drop failure_logs table."""
    op.drop_index('ix_failure_logs_created_at', 'failure_logs')
    op.drop_index('ix_failure_logs_next_retry', 'failure_logs')
    op.drop_index('ix_failure_logs_status', 'failure_logs')
    op.drop_index('ix_failure_logs_service', 'failure_logs')
    op.drop_table('failure_logs')
