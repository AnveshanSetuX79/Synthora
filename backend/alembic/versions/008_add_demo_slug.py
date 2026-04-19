"""add demo slug

Revision ID: 008
Revises: 007
Create Date: 2026-04-18 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Add slug column to demo_websites table
    op.add_column('demo_websites', sa.Column('slug', sa.String(length=255), nullable=True))
    op.create_index('ix_demo_websites_slug', 'demo_websites', ['slug'])


def downgrade():
    op.drop_index('ix_demo_websites_slug', table_name='demo_websites')
    op.drop_column('demo_websites', 'slug')
