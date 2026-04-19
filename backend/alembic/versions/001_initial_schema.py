"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables with proper indexes and constraints."""
    
    # Create enum types (with conditional creation to handle re-runs)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('freelancer', 'business_owner', 'admin', 'founder');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE freelancertier AS ENUM ('New', 'Verified', 'TopRated');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE kycstatus AS ENUM ('Pending', 'Submitted', 'Approved', 'Rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE businessstatus AS ENUM ('Active', 'Contacted', 'Cold', 'Unavailable');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE opportunitytag AS ENUM ('High', 'Medium', 'Low');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE freshnessscore AS ENUM ('High', 'Medium', 'Low');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE leadcontactstatus AS ENUM ('Contacted', 'Interested', 'Negotiating', 'Closed', 'Lost', 'Cold');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE consentstatus AS ENUM ('Contacted', 'ViewedDemo', 'Consented', 'Registered', 'OptedOut');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE outreachchannel AS ENUM ('SMS', 'Email', 'WhatsApp');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE deliverystatus AS ENUM ('Sent', 'Delivered', 'Failed', 'Bounced');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE paymentflow AS ENUM ('Simplified', 'Full');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE dealstatus AS ENUM ('Pending', 'Active', 'InProgress', 'Completed', 'Disputed', 'Cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE milestonestatus AS ENUM ('Pending', 'InProgress', 'Submitted', 'Approved', 'Rejected', 'Paid');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE paymentstatus AS ENUM ('Pending', 'Processing', 'Completed', 'Failed', 'Refunded');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transactiontype AS ENUM ('Deposit', 'Release', 'Refund', 'Commission');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE messagechannel AS ENUM ('InApp', 'SMS', 'Email', 'WhatsApp');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE messagestatus AS ENUM ('Sent', 'Delivered', 'Read', 'Failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE eventtype AS ENUM ('lead_viewed', 'demo_generated', 'demo_viewed', 'message_sent', 'deal_created', 'payment_completed', 'milestone_submitted', 'milestone_approved');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE roiperiod AS ENUM ('Week', 'Month', 'Quarter', 'AllTime');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('freelancer', 'business_owner', 'admin', 'founder', name='userrole'), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('phone_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('email_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_phone', 'users', ['phone'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # Create businesses table
    op.create_table(
        'businesses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('place_id', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('rating', sa.Float, nullable=True),
        sa.Column('review_count', sa.Integer, default=0, nullable=False),
        sa.Column('has_website', sa.Boolean, default=False, nullable=False),
        sa.Column('website_url', sa.String(500), nullable=True),
        sa.Column('digital_score', sa.Integer, nullable=False),
        sa.Column('digital_score_breakdown', postgresql.JSON, nullable=True),
        sa.Column('opportunity_tag', postgresql.ENUM('High', 'Medium', 'Low', name='opportunitytag'), nullable=False),
        sa.Column('lead_priority_score', sa.Integer, nullable=False),
        sa.Column('lead_freshness_score', postgresql.ENUM('High', 'Medium', 'Low', name='freshnessscore'), default='High', nullable=False),
        sa.Column('last_verified', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('contact_count', sa.Integer, default=0, nullable=False),
        sa.Column('status', postgresql.ENUM('Active', 'Contacted', 'Cold', 'Unavailable', name='businessstatus'), default='Active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    op.create_index('ix_businesses_place_id', 'businesses', ['place_id'])
    op.create_index('ix_businesses_name', 'businesses', ['name'])
    op.create_index('ix_businesses_category', 'businesses', ['category'])
    op.create_index('ix_businesses_city', 'businesses', ['city'])
    op.create_index('ix_businesses_has_website', 'businesses', ['has_website'])
    op.create_index('ix_businesses_digital_score', 'businesses', ['digital_score'])
    op.create_index('ix_businesses_opportunity_tag', 'businesses', ['opportunity_tag'])
    op.create_index('ix_businesses_lead_priority_score', 'businesses', ['lead_priority_score'])
    op.create_index('ix_businesses_lead_freshness_score', 'businesses', ['lead_freshness_score'])
    op.create_index('ix_businesses_last_verified', 'businesses', ['last_verified'])
    op.create_index('ix_businesses_status', 'businesses', ['status'])
    op.create_index('ix_businesses_created_at', 'businesses', ['created_at'])
    op.create_index('ix_businesses_map_filter', 'businesses', ['city', 'category', 'digital_score', 'status'])

    # Create freelancers table
    op.create_table(
        'freelancers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('portfolio_url', sa.String(500), nullable=True),
        sa.Column('tier', postgresql.ENUM('New', 'Verified', 'TopRated', name='freelancertier'), default='New', nullable=False),
        sa.Column('daily_limit', sa.Integer, default=3, nullable=False),
        sa.Column('remaining_contacts', sa.Integer, default=3, nullable=False),
        sa.Column('kyc_status', postgresql.ENUM('Pending', 'Submitted', 'Approved', 'Rejected', name='kycstatus'), default='Pending', nullable=False),
        sa.Column('kyc_documents', sa.String(1000), nullable=True),
        sa.Column('average_rating', sa.Float, default=0.0, nullable=False),
        sa.Column('review_count', sa.Integer, default=0, nullable=False),
        sa.Column('conversion_rate', sa.Float, default=0.0, nullable=False),
        sa.Column('response_rate', sa.Float, default=0.0, nullable=False),
        sa.Column('total_earnings', sa.Integer, default=0, nullable=False),
        sa.Column('deals_closed', sa.Integer, default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_freelancers_user_id', 'freelancers', ['user_id'])
    op.create_index('ix_freelancers_tier', 'freelancers', ['tier'])
    op.create_index('ix_freelancers_kyc_status', 'freelancers', ['kyc_status'])

    # Create business_owners table
    op.create_table(
        'business_owners',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, unique=True),
        sa.Column('business_id', sa.String(36), nullable=True),
        sa.Column('owner_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='SET NULL')
    )
    op.create_index('ix_business_owners_user_id', 'business_owners', ['user_id'])
    op.create_index('ix_business_owners_business_id', 'business_owners', ['business_id'])

    # Create admins table
    op.create_table(
        'admins',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('permissions', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_admins_user_id', 'admins', ['user_id'])

    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('business_id', sa.String(36), nullable=False, unique=True),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('freshness', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('exclusivity_window_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['freelancers.id'], ondelete='SET NULL')
    )
    op.create_index('ix_leads_business_id', 'leads', ['business_id'])
    op.create_index('ix_leads_score', 'leads', ['score'])
    op.create_index('ix_leads_freshness', 'leads', ['freshness'])
    op.create_index('ix_leads_status', 'leads', ['status'])
    op.create_index('ix_leads_assigned_to', 'leads', ['assigned_to'])
    op.create_index('ix_leads_exclusivity_window_expires', 'leads', ['exclusivity_window_expires'])

    # Create lead_contacts table
    op.create_table(
        'lead_contacts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('business_id', sa.String(36), nullable=False),
        sa.Column('freelancer_id', sa.String(36), nullable=False),
        sa.Column('status', postgresql.ENUM('Contacted', 'Interested', 'Negotiating', 'Closed', 'Lost', 'Cold', name='leadcontactstatus'), default='Contacted', nullable=False),
        sa.Column('exclusivity_active', sa.Boolean, default=True, nullable=False),
        sa.Column('exclusivity_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('first_contact_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_contact_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('follow_up_count', sa.Integer, default=0, nullable=False),
        sa.Column('consent_status', postgresql.ENUM('Contacted', 'ViewedDemo', 'Consented', 'Registered', 'OptedOut', name='consentstatus'), default='Contacted', nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['freelancer_id'], ['freelancers.id'], ondelete='CASCADE')
    )
    op.create_index('ix_lead_contacts_business_id', 'lead_contacts', ['business_id'])
    op.create_index('ix_lead_contacts_freelancer_id', 'lead_contacts', ['freelancer_id'])
    op.create_index('ix_lead_contacts_status', 'lead_contacts', ['status'])
    op.create_index('ix_lead_contacts_exclusivity_expires_at', 'lead_contacts', ['exclusivity_expires_at'])
    op.create_index('ix_lead_contacts_first_contact_at', 'lead_contacts', ['first_contact_at'])
    op.create_index('ix_lead_contacts_consent_status', 'lead_contacts', ['consent_status'])

    # Create outreach_messages table
    op.create_table(
        'outreach_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('lead_contact_id', sa.String(36), nullable=False),
        sa.Column('channel', postgresql.ENUM('SMS', 'Email', 'WhatsApp', name='outreachchannel'), nullable=False),
        sa.Column('template_id', sa.String(100), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('delivery_status', postgresql.ENUM('Sent', 'Delivered', 'Failed', 'Bounced', name='deliverystatus'), default='Sent', nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opted_out', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['lead_contact_id'], ['lead_contacts.id'], ondelete='CASCADE')
    )
    op.create_index('ix_outreach_messages_lead_contact_id', 'outreach_messages', ['lead_contact_id'])
    op.create_index('ix_outreach_messages_channel', 'outreach_messages', ['channel'])
    op.create_index('ix_outreach_messages_delivery_status', 'outreach_messages', ['delivery_status'])
    op.create_index('ix_outreach_messages_sent_at', 'outreach_messages', ['sent_at'])
    op.create_index('ix_outreach_messages_opted_out', 'outreach_messages', ['opted_out'])

    # Create demo_websites table
    op.create_table(
        'demo_websites',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('business_id', sa.String(36), nullable=False),
        sa.Column('template_type', sa.String(100), nullable=False),
        sa.Column('url', sa.String(500), nullable=False, unique=True),
        sa.Column('cached', sa.Boolean, default=True, nullable=False),
        sa.Column('view_count', sa.Integer, default=0, nullable=False),
        sa.Column('unique_visitors', sa.Integer, default=0, nullable=False),
        sa.Column('avg_time_on_page', sa.Integer, default=0, nullable=False),
        sa.Column('claim_clicks', sa.Integer, default=0, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE')
    )
    op.create_index('ix_demo_websites_business_id', 'demo_websites', ['business_id'])
    op.create_index('ix_demo_websites_url', 'demo_websites', ['url'])
    op.create_index('ix_demo_websites_generated_at', 'demo_websites', ['generated_at'])

    # Create deals table
    op.create_table(
        'deals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('freelancer_id', sa.String(36), nullable=False),
        sa.Column('business_id', sa.String(36), nullable=False),
        sa.Column('business_owner_id', sa.String(36), nullable=True),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('payment_flow', postgresql.ENUM('Simplified', 'Full', name='paymentflow'), default='Simplified', nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'Active', 'InProgress', 'Completed', 'Disputed', 'Cancelled', name='dealstatus'), default='Pending', nullable=False),
        sa.Column('package_type', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['freelancer_id'], ['freelancers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['business_owner_id'], ['business_owners.id'], ondelete='CASCADE')
    )
    op.create_index('ix_deals_freelancer_id', 'deals', ['freelancer_id'])
    op.create_index('ix_deals_business_id', 'deals', ['business_id'])
    op.create_index('ix_deals_business_owner_id', 'deals', ['business_owner_id'])
    op.create_index('ix_deals_status', 'deals', ['status'])
    op.create_index('ix_deals_created_at', 'deals', ['created_at'])

    # Create milestones table
    op.create_table(
        'milestones',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('deal_id', sa.String(36), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('percentage', sa.Integer, nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'InProgress', 'Submitted', 'Approved', 'Rejected', 'Paid', name='milestonestatus'), default='Pending', nullable=False),
        sa.Column('deliverables', postgresql.JSON, nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE')
    )
    op.create_index('ix_milestones_deal_id', 'milestones', ['deal_id'])
    op.create_index('ix_milestones_status', 'milestones', ['status'])
    op.create_index('ix_milestones_paid_at', 'milestones', ['paid_at'])

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('deal_id', sa.String(36), nullable=False),
        sa.Column('milestone_id', sa.String(36), nullable=True),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('commission', sa.Integer, default=0, nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'Processing', 'Completed', 'Failed', 'Refunded', name='paymentstatus'), default='Pending', nullable=False),
        sa.Column('razorpay_order_id', sa.String(255), nullable=True, unique=True),
        sa.Column('razorpay_payment_id', sa.String(255), nullable=True, unique=True),
        sa.Column('razorpay_signature', sa.String(500), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='SET NULL')
    )
    op.create_index('ix_payments_deal_id', 'payments', ['deal_id'])
    op.create_index('ix_payments_milestone_id', 'payments', ['milestone_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_razorpay_order_id', 'payments', ['razorpay_order_id'])
    op.create_index('ix_payments_razorpay_payment_id', 'payments', ['razorpay_payment_id'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('payment_id', sa.String(36), nullable=False),
        sa.Column('deal_id', sa.String(36), nullable=False),
        sa.Column('milestone_id', sa.String(36), nullable=True),
        sa.Column('type', postgresql.ENUM('Deposit', 'Release', 'Refund', 'Commission', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('commission', sa.Integer, default=0, nullable=False),
        sa.Column('status', postgresql.ENUM('Pending', 'Processing', 'Completed', 'Failed', 'Refunded', name='paymentstatus'), default='Pending', nullable=False),
        sa.Column('payment_provider_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='SET NULL')
    )
    op.create_index('ix_transactions_payment_id', 'transactions', ['payment_id'])
    op.create_index('ix_transactions_deal_id', 'transactions', ['deal_id'])
    op.create_index('ix_transactions_type', 'transactions', ['type'])
    op.create_index('ix_transactions_status', 'transactions', ['status'])
    op.create_index('ix_transactions_payment_provider_id', 'transactions', ['payment_provider_id'])
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('freelancer_id', sa.String(36), nullable=False),
        sa.Column('business_owner_id', sa.String(36), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['freelancer_id'], ['freelancers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['business_owner_id'], ['business_owners.id'], ondelete='CASCADE')
    )
    op.create_index('ix_conversations_freelancer_id', 'conversations', ['freelancer_id'])
    op.create_index('ix_conversations_business_owner_id', 'conversations', ['business_owner_id'])
    op.create_index('ix_conversations_last_message_at', 'conversations', ['last_message_at'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('conversation_id', sa.String(36), nullable=False),
        sa.Column('sender_id', sa.String(36), nullable=True),
        sa.Column('recipient_id', sa.String(36), nullable=True),
        sa.Column('channel', postgresql.ENUM('InApp', 'SMS', 'Email', 'WhatsApp', name='messagechannel'), default='InApp', nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('attachments', postgresql.JSON, nullable=True),
        sa.Column('status', postgresql.ENUM('Sent', 'Delivered', 'Read', 'Failed', name='messagestatus'), default='Sent', nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['freelancers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['business_owners.id'], ondelete='CASCADE')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_recipient_id', 'messages', ['recipient_id'])
    op.create_index('ix_messages_channel', 'messages', ['channel'])
    op.create_index('ix_messages_status', 'messages', ['status'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', postgresql.ENUM('lead_viewed', 'demo_generated', 'demo_viewed', 'message_sent', 'deal_created', 'payment_completed', 'milestone_submitted', 'milestone_approved', name='eventtype'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_user_id', 'analytics_events', ['user_id'])
    op.create_index('ix_analytics_events_timestamp', 'analytics_events', ['timestamp'])

    # Create freelancer_roi table
    op.create_table(
        'freelancer_roi',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('freelancer_id', sa.String(36), nullable=False),
        sa.Column('period', postgresql.ENUM('Week', 'Month', 'Quarter', 'AllTime', name='roiperiod'), nullable=False),
        sa.Column('total_earnings', sa.Integer, default=0, nullable=False),
        sa.Column('leads_used', sa.Integer, default=0, nullable=False),
        sa.Column('cost_per_acquisition', sa.Integer, default=0, nullable=False),
        sa.Column('win_rate', sa.Float, default=0.0, nullable=False),
        sa.Column('avg_time_to_close', sa.Integer, default=0, nullable=False),
        sa.Column('lead_quality_score', sa.Float, default=0.0, nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['freelancer_id'], ['freelancers.id'], ondelete='CASCADE')
    )
    op.create_index('ix_freelancer_roi_freelancer_id', 'freelancer_roi', ['freelancer_id'])
    op.create_index('ix_freelancer_roi_period', 'freelancer_roi', ['period'])
    op.create_index('ix_freelancer_roi_calculated_at', 'freelancer_roi', ['calculated_at'])

    # Create conversion_intelligence table
    op.create_table(
        'conversion_intelligence',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('business_characteristics', postgresql.JSON, nullable=False),
        sa.Column('conversion_rate', sa.Float, nullable=False),
        sa.Column('avg_deal_value', sa.Integer, nullable=False),
        sa.Column('avg_time_to_close', sa.Integer, nullable=False),
        sa.Column('top_objections', postgresql.JSON, nullable=True),
        sa.Column('optimal_pricing', sa.Integer, nullable=False),
        sa.Column('sample_size', sa.Integer, nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    op.create_index('ix_conversion_intelligence_category', 'conversion_intelligence', ['category'])
    op.create_index('ix_conversion_intelligence_last_updated', 'conversion_intelligence', ['last_updated'])


def downgrade() -> None:
    """Drop all tables and enum types."""
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('conversion_intelligence')
    op.drop_table('freelancer_roi')
    op.drop_table('analytics_events')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('transactions')
    op.drop_table('payments')
    op.drop_table('milestones')
    op.drop_table('deals')
    op.drop_table('demo_websites')
    op.drop_table('outreach_messages')
    op.drop_table('lead_contacts')
    op.drop_table('leads')
    op.drop_table('admins')
    op.drop_table('business_owners')
    op.drop_table('freelancers')
    op.drop_table('businesses')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS roiperiod")
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS messagestatus")
    op.execute("DROP TYPE IF EXISTS messagechannel")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS milestonestatus")
    op.execute("DROP TYPE IF EXISTS dealstatus")
    op.execute("DROP TYPE IF EXISTS paymentflow")
    op.execute("DROP TYPE IF EXISTS deliverystatus")
    op.execute("DROP TYPE IF EXISTS outreachchannel")
    op.execute("DROP TYPE IF EXISTS consentstatus")
    op.execute("DROP TYPE IF EXISTS leadcontactstatus")
    op.execute("DROP TYPE IF EXISTS freshnessscore")
    op.execute("DROP TYPE IF EXISTS opportunitytag")
    op.execute("DROP TYPE IF EXISTS businessstatus")
    op.execute("DROP TYPE IF EXISTS kycstatus")
    op.execute("DROP TYPE IF EXISTS freelancertier")
    op.execute("DROP TYPE IF EXISTS userrole")
