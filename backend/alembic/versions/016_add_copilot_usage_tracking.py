"""Add AI copilot usage tracking

Revision ID: 016
Revises: 015
Create Date: 2026-04-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    """Add copilot usage tracking to lead_contacts."""
    op.add_column('lead_contacts', sa.Column('copilot_uses', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('lead_contacts', sa.Column('last_copilot_use', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """Remove copilot usage tracking."""
    op.drop_column('lead_contacts', 'last_copilot_use')
    op.drop_column('lead_contacts', 'copilot_uses')
