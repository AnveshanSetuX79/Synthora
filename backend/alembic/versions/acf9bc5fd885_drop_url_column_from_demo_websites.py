"""drop_url_column_from_demo_websites

Revision ID: acf9bc5fd885
Revises: 0f835842b85e
Create Date: 2026-04-18 14:20:06.655108

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acf9bc5fd885'
down_revision = '0f835842b85e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop old columns from demo_websites table."""
    # Check if columns exist and drop them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('demo_websites')]
    
    # Drop old columns if they exist
    if 'url' in columns:
        op.drop_column('demo_websites', 'url')
    
    if 'cached' in columns:
        op.drop_column('demo_websites', 'cached')
    
    if 'unique_visitors' in columns:
        op.drop_column('demo_websites', 'unique_visitors')
    
    if 'avg_time_on_page' in columns:
        op.drop_column('demo_websites', 'avg_time_on_page')
    
    if 'generated_at' in columns:
        op.drop_column('demo_websites', 'generated_at')


def downgrade() -> None:
    """Add back old columns."""
    op.add_column('demo_websites', sa.Column('url', sa.String(500), nullable=True))
    op.add_column('demo_websites', sa.Column('cached', sa.Boolean, default=True, nullable=True))
    op.add_column('demo_websites', sa.Column('unique_visitors', sa.Integer, default=0, nullable=True))
    op.add_column('demo_websites', sa.Column('avg_time_on_page', sa.Integer, default=0, nullable=True))
    op.add_column('demo_websites', sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True))

