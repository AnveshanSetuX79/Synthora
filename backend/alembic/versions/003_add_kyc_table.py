"""Add KYC documents table

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create kyc_documents table
    op.create_table(
        'kyc_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('freelancer_id', sa.String(36), sa.ForeignKey('freelancers.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_number', sa.String(100), nullable=False),
        sa.Column('document_url', sa.String(500), nullable=True),
        sa.Column('bank_account_number', sa.String(50), nullable=True),
        sa.Column('bank_ifsc_code', sa.String(20), nullable=True),
        sa.Column('bank_account_holder_name', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('verified_by', sa.String(36), nullable=True),
        sa.Column('razorpay_account_id', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('razorpay_account_status', sa.String(50), nullable=True),
        sa.Column('additional_data', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_table('kyc_documents')
