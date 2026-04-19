"""Update demo_websites table schema

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update demo_websites table to store HTML content."""
    
    # Drop old columns
    op.drop_column('demo_websites', 'url')
    op.drop_column('demo_websites', 'cached')
    op.drop_column('demo_websites', 'unique_visitors')
    op.drop_column('demo_websites', 'avg_time_on_page')
    op.drop_column('demo_websites', 'generated_at')
    
    # Add new columns
    op.add_column('demo_websites', sa.Column('html_content', sa.Text, nullable=True))
    op.add_column('demo_websites', sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('demo_websites', sa.Column('created_by', sa.String(36), nullable=True))
    
    # Add foreign key for created_by
    op.create_foreign_key(
        'fk_demo_websites_created_by',
        'demo_websites',
        'users',
        ['created_by'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Make html_content non-nullable after adding it
    # (we added it as nullable first to allow existing rows, but there shouldn't be any)
    op.alter_column('demo_websites', 'html_content', nullable=False)


def downgrade() -> None:
    """Revert demo_websites table to original schema."""
    
    # Drop new columns
    op.drop_constraint('fk_demo_websites_created_by', 'demo_websites', type_='foreignkey')
    op.drop_column('demo_websites', 'created_by')
    op.drop_column('demo_websites', 'last_viewed_at')
    op.drop_column('demo_websites', 'html_content')
    
    # Add back old columns
    op.add_column('demo_websites', sa.Column('url', sa.String(500), nullable=False, unique=True))
    op.add_column('demo_websites', sa.Column('cached', sa.Boolean, default=True, nullable=False))
    op.add_column('demo_websites', sa.Column('unique_visitors', sa.Integer, default=0, nullable=False))
    op.add_column('demo_websites', sa.Column('avg_time_on_page', sa.Integer, default=0, nullable=False))
    op.add_column('demo_websites', sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    
    # Recreate index
    op.create_index('ix_demo_websites_url', 'demo_websites', ['url'])
    op.create_index('ix_demo_websites_generated_at', 'demo_websites', ['generated_at'])
