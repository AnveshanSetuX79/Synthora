"""fix_demo_websites_add_html_content

Revision ID: 0f835842b85e
Revises: 008
Create Date: 2026-04-18 14:11:58.630939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f835842b85e'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add html_content column if it doesn't exist."""
    # Check if column exists and add it if not
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('demo_websites')]
    
    if 'html_content' not in columns:
        op.add_column('demo_websites', sa.Column('html_content', sa.Text(), nullable=True))
        # Set a default value for existing rows
        op.execute("UPDATE demo_websites SET html_content = '<html><body>Demo content</body></html>' WHERE html_content IS NULL")
        # Make it non-nullable
        op.alter_column('demo_websites', 'html_content', nullable=False)
    
    if 'last_viewed_at' not in columns:
        op.add_column('demo_websites', sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True))
    
    if 'created_by' not in columns:
        op.add_column('demo_websites', sa.Column('created_by', sa.String(36), nullable=True))
        # Try to add foreign key if it doesn't exist
        try:
            op.create_foreign_key(
                'fk_demo_websites_created_by',
                'demo_websites',
                'users',
                ['created_by'],
                ['id'],
                ondelete='SET NULL'
            )
        except:
            pass  # Foreign key might already exist


def downgrade() -> None:
    """Remove html_content column."""
    op.drop_column('demo_websites', 'html_content')
    op.drop_column('demo_websites', 'last_viewed_at')
    try:
        op.drop_constraint('fk_demo_websites_created_by', 'demo_websites', type_='foreignkey')
    except:
        pass
    op.drop_column('demo_websites', 'created_by')

