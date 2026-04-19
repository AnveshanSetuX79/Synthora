"""Add AI enrichment fields to business_insights

Revision ID: 015_add_ai_enrichment
Revises: 014_add_performance_indexes
Create Date: 2026-04-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    """Add AI enrichment fields to business_insights table."""
    
    # Add AI enrichment fields
    op.add_column('business_insights', sa.Column('ai_description', sa.Text(), nullable=True))
    op.add_column('business_insights', sa.Column('ai_specialties', JSON, nullable=True))
    op.add_column('business_insights', sa.Column('ai_target_customers', JSON, nullable=True))
    op.add_column('business_insights', sa.Column('ai_pain_points', JSON, nullable=True))
    op.add_column('business_insights', sa.Column('ai_recommended_solutions', JSON, nullable=True))
    op.add_column('business_insights', sa.Column('ai_competitive_advantages', JSON, nullable=True))
    op.add_column('business_insights', sa.Column('ai_digital_maturity', sa.String(50), nullable=True))
    op.add_column('business_insights', sa.Column('ai_growth_potential', sa.String(50), nullable=True))
    op.add_column('business_insights', sa.Column('ai_estimated_size', sa.String(50), nullable=True))
    op.add_column('business_insights', sa.Column('ai_online_presence_score', sa.Integer(), nullable=True))
    op.add_column('business_insights', sa.Column('ai_urgency_score', sa.Integer(), nullable=True))
    op.add_column('business_insights', sa.Column('ai_enrichment_confidence', sa.Float(), nullable=True))
    op.add_column('business_insights', sa.Column('ai_enriched_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('business_insights', sa.Column('ai_pitch_suggestions', JSON, nullable=True))


def downgrade():
    """Remove AI enrichment fields."""
    op.drop_column('business_insights', 'ai_pitch_suggestions')
    op.drop_column('business_insights', 'ai_enriched_at')
    op.drop_column('business_insights', 'ai_enrichment_confidence')
    op.drop_column('business_insights', 'ai_urgency_score')
    op.drop_column('business_insights', 'ai_online_presence_score')
    op.drop_column('business_insights', 'ai_estimated_size')
    op.drop_column('business_insights', 'ai_growth_potential')
    op.drop_column('business_insights', 'ai_digital_maturity')
    op.drop_column('business_insights', 'ai_competitive_advantages')
    op.drop_column('business_insights', 'ai_recommended_solutions')
    op.drop_column('business_insights', 'ai_pain_points')
    op.drop_column('business_insights', 'ai_target_customers')
    op.drop_column('business_insights', 'ai_specialties')
    op.drop_column('business_insights', 'ai_description')
