"""Fix NULL copilot_uses values

Revision ID: 018
Revises: 017
Create Date: 2026-04-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    """Update NULL copilot_uses to 0."""
    # Update any NULL values to 0
    op.execute("""
        UPDATE lead_contacts 
        SET copilot_uses = 0 
        WHERE copilot_uses IS NULL
    """)


def downgrade():
    """No downgrade needed."""
    pass
