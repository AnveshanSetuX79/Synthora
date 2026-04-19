"""Add follow_up_count to lead_contacts

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add follow_up_count column to lead_contacts table."""
    op.add_column('lead_contacts', 
        sa.Column('follow_up_count', sa.Integer(), nullable=False, server_default='0')
    )


def downgrade():
    """Remove follow_up_count column from lead_contacts table."""
    op.drop_column('lead_contacts', 'follow_up_count')
