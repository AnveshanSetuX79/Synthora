"""Convert all enum values to lowercase

Revision ID: 004
Revises: 003
Create Date: 2026-04-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Convert all enum columns to use String type and lowercase values.
    
    This migration:
    1. Changes all enum columns to VARCHAR(50)
    2. Updates existing data to lowercase
    """
    
    # Users table - role column
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)")
    op.execute("UPDATE users SET role = 'freelancer' WHERE role IN ('FREELANCER', 'Freelancer')")
    op.execute("UPDATE users SET role = 'businessowner' WHERE role IN ('BUSINESS_OWNER', 'BusinessOwner', 'business_owner')")
    op.execute("UPDATE users SET role = 'admin' WHERE role IN ('ADMIN', 'Admin')")
    op.execute("UPDATE users SET role = 'founder' WHERE role IN ('FOUNDER', 'Founder')")
    
    # Freelancers table - tier column
    op.execute("ALTER TABLE freelancers ALTER COLUMN tier TYPE VARCHAR(50)")
    op.execute("UPDATE freelancers SET tier = 'new' WHERE tier IN ('FREE', 'Free', 'NEW', 'New')")
    op.execute("UPDATE freelancers SET tier = 'verified' WHERE tier IN ('BASIC', 'Basic', 'VERIFIED', 'Verified')")
    op.execute("UPDATE freelancers SET tier = 'toprated' WHERE tier IN ('PRO', 'Pro', 'TOPRATED', 'TopRated', 'top_rated')")
    
    # Deals table - status and payment_flow columns
    op.execute("ALTER TABLE deals ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE deals SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE deals SET status = 'active' WHERE status IN ('ACTIVE', 'Active')")
    op.execute("UPDATE deals SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS', 'in_progress')")
    op.execute("UPDATE deals SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE deals SET status = 'disputed' WHERE status IN ('DISPUTED', 'Disputed')")
    op.execute("UPDATE deals SET status = 'cancelled' WHERE status IN ('CANCELLED', 'Cancelled')")
    
    op.execute("ALTER TABLE deals ALTER COLUMN payment_flow TYPE VARCHAR(50)")
    op.execute("UPDATE deals SET payment_flow = 'simplified' WHERE payment_flow IN ('SIMPLIFIED', 'Simplified')")
    op.execute("UPDATE deals SET payment_flow = 'full' WHERE payment_flow IN ('FULL', 'Full')")
    
    # Milestones table - status column
    op.execute("ALTER TABLE milestones ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE milestones SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE milestones SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS', 'in_progress')")
    op.execute("UPDATE milestones SET status = 'submitted' WHERE status IN ('SUBMITTED', 'Submitted')")
    op.execute("UPDATE milestones SET status = 'approved' WHERE status IN ('APPROVED', 'Approved')")
    op.execute("UPDATE milestones SET status = 'rejected' WHERE status IN ('REJECTED', 'Rejected')")
    op.execute("UPDATE milestones SET status = 'paid' WHERE status IN ('PAID', 'Paid')")
    
    # Payments table - status column
    op.execute("ALTER TABLE payments ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE payments SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE payments SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')")
    op.execute("UPDATE payments SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE payments SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    op.execute("UPDATE payments SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')")
    
    # Transactions table - type and status columns
    op.execute("ALTER TABLE transactions ALTER COLUMN type TYPE VARCHAR(50)")
    op.execute("UPDATE transactions SET type = 'deposit' WHERE type IN ('DEPOSIT', 'Deposit')")
    op.execute("UPDATE transactions SET type = 'release' WHERE type IN ('RELEASE', 'Release')")
    op.execute("UPDATE transactions SET type = 'refund' WHERE type IN ('REFUND', 'Refund')")
    op.execute("UPDATE transactions SET type = 'commission' WHERE type IN ('COMMISSION', 'Commission')")
    
    op.execute("ALTER TABLE transactions ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE transactions SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE transactions SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')")
    op.execute("UPDATE transactions SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE transactions SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    op.execute("UPDATE transactions SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')")
    
    # Leads table - source and status columns (if they exist)
    try:
        op.execute("ALTER TABLE leads ALTER COLUMN source TYPE VARCHAR(50)")
        op.execute("UPDATE leads SET source = 'google' WHERE source IN ('GOOGLE', 'Google')")
        op.execute("UPDATE leads SET source = 'manual' WHERE source IN ('MANUAL', 'Manual')")
        op.execute("UPDATE leads SET source = 'referral' WHERE source IN ('REFERRAL', 'Referral')")
        op.execute("UPDATE leads SET source = 'import' WHERE source IN ('IMPORT', 'Import')")
        
        op.execute("ALTER TABLE leads ALTER COLUMN status TYPE VARCHAR(50)")
        op.execute("UPDATE leads SET status = 'new' WHERE status IN ('NEW', 'New')")
        op.execute("UPDATE leads SET status = 'assigned' WHERE status IN ('ASSIGNED', 'Assigned')")
        op.execute("UPDATE leads SET status = 'contacted' WHERE status IN ('CONTACTED', 'Contacted')")
        op.execute("UPDATE leads SET status = 'qualified' WHERE status IN ('QUALIFIED', 'Qualified')")
        op.execute("UPDATE leads SET status = 'converted' WHERE status IN ('CONVERTED', 'Converted')")
        op.execute("UPDATE leads SET status = 'lost' WHERE status IN ('LOST', 'Lost')")
        op.execute("UPDATE leads SET status = 'archived' WHERE status IN ('ARCHIVED', 'Archived')")
    except:
        pass
    
    # Lead_contacts table - status and consent_status columns
    try:
        op.execute("ALTER TABLE lead_contacts ALTER COLUMN status TYPE VARCHAR(50)")
        op.execute("UPDATE lead_contacts SET status = 'contacted' WHERE status IN ('CONTACTED', 'Contacted')")
        op.execute("UPDATE lead_contacts SET status = 'interested' WHERE status IN ('INTERESTED', 'Interested')")
        op.execute("UPDATE lead_contacts SET status = 'negotiating' WHERE status IN ('NEGOTIATING', 'Negotiating')")
        op.execute("UPDATE lead_contacts SET status = 'closed' WHERE status IN ('CLOSED', 'Closed')")
        op.execute("UPDATE lead_contacts SET status = 'lost' WHERE status IN ('LOST', 'Lost')")
        op.execute("UPDATE lead_contacts SET status = 'cold' WHERE status IN ('COLD', 'Cold')")
        
        op.execute("ALTER TABLE lead_contacts ALTER COLUMN consent_status TYPE VARCHAR(50)")
        op.execute("UPDATE lead_contacts SET consent_status = 'contacted' WHERE consent_status IN ('CONTACTED', 'Contacted')")
        op.execute("UPDATE lead_contacts SET consent_status = 'vieweddemo' WHERE consent_status IN ('VIEWED_DEMO', 'ViewedDemo', 'VIEWEDDEMO', 'viewed_demo')")
        op.execute("UPDATE lead_contacts SET consent_status = 'consented' WHERE consent_status IN ('CONSENTED', 'Consented')")
        op.execute("UPDATE lead_contacts SET consent_status = 'registered' WHERE consent_status IN ('REGISTERED', 'Registered')")
        op.execute("UPDATE lead_contacts SET consent_status = 'optedout' WHERE consent_status IN ('OPTED_OUT', 'OptedOut', 'OPTEDOUT', 'opted_out')")
    except:
        pass
    
    # Outreach_messages table - channel and delivery_status columns
    try:
        op.execute("ALTER TABLE outreach_messages ALTER COLUMN channel TYPE VARCHAR(50)")
        op.execute("UPDATE outreach_messages SET channel = 'sms' WHERE channel IN ('SMS', 'Sms')")
        op.execute("UPDATE outreach_messages SET channel = 'email' WHERE channel IN ('EMAIL', 'Email')")
        op.execute("UPDATE outreach_messages SET channel = 'whatsapp' WHERE channel IN ('WHATSAPP', 'WhatsApp')")
        
        op.execute("ALTER TABLE outreach_messages ALTER COLUMN delivery_status TYPE VARCHAR(50)")
        op.execute("UPDATE outreach_messages SET delivery_status = 'sent' WHERE delivery_status IN ('SENT', 'Sent')")
        op.execute("UPDATE outreach_messages SET delivery_status = 'delivered' WHERE delivery_status IN ('DELIVERED', 'Delivered')")
        op.execute("UPDATE outreach_messages SET delivery_status = 'failed' WHERE delivery_status IN ('FAILED', 'Failed')")
        op.execute("UPDATE outreach_messages SET delivery_status = 'bounced' WHERE delivery_status IN ('BOUNCED', 'Bounced')")
    except:
        pass
    
    # Lead_activities table - activity_type column
    try:
        op.execute("ALTER TABLE lead_activities ALTER COLUMN activity_type TYPE VARCHAR(50)")
        op.execute("UPDATE lead_activities SET activity_type = 'followup' WHERE activity_type IN ('FOLLOW_UP', 'FollowUp', 'follow_up')")
        op.execute("UPDATE lead_activities SET activity_type = 'call' WHERE activity_type IN ('CALL', 'Call')")
        op.execute("UPDATE lead_activities SET activity_type = 'meeting' WHERE activity_type IN ('MEETING', 'Meeting')")
        op.execute("UPDATE lead_activities SET activity_type = 'email' WHERE activity_type IN ('EMAIL', 'Email')")
        op.execute("UPDATE lead_activities SET activity_type = 'note' WHERE activity_type IN ('NOTE', 'Note')")
        op.execute("UPDATE lead_activities SET activity_type = 'statuschange' WHERE activity_type IN ('STATUS_CHANGE', 'StatusChange', 'status_change')")
    except:
        pass
    
    # Messages table - channel and status columns
    try:
        op.execute("ALTER TABLE messages ALTER COLUMN channel TYPE VARCHAR(50)")
        op.execute("UPDATE messages SET channel = 'inapp' WHERE channel IN ('IN_APP', 'InApp', 'INAPP', 'in_app')")
        op.execute("UPDATE messages SET channel = 'sms' WHERE channel IN ('SMS', 'Sms')")
        op.execute("UPDATE messages SET channel = 'email' WHERE channel IN ('EMAIL', 'Email')")
        op.execute("UPDATE messages SET channel = 'whatsapp' WHERE channel IN ('WHATSAPP', 'WhatsApp')")
        
        op.execute("ALTER TABLE messages ALTER COLUMN status TYPE VARCHAR(50)")
        op.execute("UPDATE messages SET status = 'sent' WHERE status IN ('SENT', 'Sent')")
        op.execute("UPDATE messages SET status = 'delivered' WHERE status IN ('DELIVERED', 'Delivered')")
        op.execute("UPDATE messages SET status = 'read' WHERE status IN ('READ', 'Read')")
        op.execute("UPDATE messages SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    except:
        pass
    
    # Campaigns table - type and status columns
    try:
        op.execute("ALTER TABLE campaigns ALTER COLUMN type TYPE VARCHAR(50)")
        op.execute("UPDATE campaigns SET type = 'googlediscovery' WHERE type IN ('GOOGLE_DISCOVERY', 'GoogleDiscovery', 'google_discovery')")
        op.execute("UPDATE campaigns SET type = 'manualoutreach' WHERE type IN ('MANUAL_OUTREACH', 'ManualOutreach', 'manual_outreach')")
        op.execute("UPDATE campaigns SET type = 'referral' WHERE type IN ('REFERRAL', 'Referral')")
        op.execute("UPDATE campaigns SET type = 'retargeting' WHERE type IN ('RETARGETING', 'Retargeting')")
        
        op.execute("ALTER TABLE campaigns ALTER COLUMN status TYPE VARCHAR(50)")
        op.execute("UPDATE campaigns SET status = 'draft' WHERE status IN ('DRAFT', 'Draft')")
        op.execute("UPDATE campaigns SET status = 'active' WHERE status IN ('ACTIVE', 'Active')")
        op.execute("UPDATE campaigns SET status = 'paused' WHERE status IN ('PAUSED', 'Paused')")
        op.execute("UPDATE campaigns SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
        op.execute("UPDATE campaigns SET status = 'archived' WHERE status IN ('ARCHIVED', 'Archived')")
    except:
        pass
    
    # Freelancer_roi table - period column
    try:
        op.execute("ALTER TABLE freelancer_roi ALTER COLUMN period TYPE VARCHAR(50)")
        op.execute("UPDATE freelancer_roi SET period = 'week' WHERE period IN ('WEEK', 'Week')")
        op.execute("UPDATE freelancer_roi SET period = 'month' WHERE period IN ('MONTH', 'Month')")
        op.execute("UPDATE freelancer_roi SET period = 'quarter' WHERE period IN ('QUARTER', 'Quarter')")
        op.execute("UPDATE freelancer_roi SET period = 'alltime' WHERE period IN ('ALL_TIME', 'AllTime', 'ALLTIME', 'all_time')")
    except:
        pass
    
    # KYC_documents table - document_type and status columns
    try:
        op.execute("ALTER TABLE kyc_documents ALTER COLUMN document_type TYPE VARCHAR(50)")
        op.execute("UPDATE kyc_documents SET document_type = 'aadhaar' WHERE document_type IN ('AADHAAR', 'Aadhaar')")
        op.execute("UPDATE kyc_documents SET document_type = 'pan' WHERE document_type IN ('PAN', 'Pan')")
        op.execute("UPDATE kyc_documents SET document_type = 'drivinglicense' WHERE document_type IN ('DRIVING_LICENSE', 'DrivingLicense', 'driving_license')")
        op.execute("UPDATE kyc_documents SET document_type = 'passport' WHERE document_type IN ('PASSPORT', 'Passport')")
        op.execute("UPDATE kyc_documents SET document_type = 'bankaccount' WHERE document_type IN ('BANK_ACCOUNT', 'BankAccount', 'bank_account')")
        
        op.execute("ALTER TABLE kyc_documents ALTER COLUMN status TYPE VARCHAR(50)")
        op.execute("UPDATE kyc_documents SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
        op.execute("UPDATE kyc_documents SET status = 'submitted' WHERE status IN ('SUBMITTED', 'Submitted')")
        op.execute("UPDATE kyc_documents SET status = 'underreview' WHERE status IN ('UNDER_REVIEW', 'UnderReview', 'under_review')")
        op.execute("UPDATE kyc_documents SET status = 'approved' WHERE status IN ('APPROVED', 'Approved')")
        op.execute("UPDATE kyc_documents SET status = 'rejected' WHERE status IN ('REJECTED', 'Rejected')")
    except:
        pass


def downgrade():
    """Revert enum values back to PascalCase/CamelCase."""
    
    # This is a one-way migration for simplicity
    # If you need to revert, you would need to implement the reverse logic
    pass

    
    # Freelancers table - tier column
    op.execute("ALTER TABLE freelancers ALTER COLUMN tier TYPE VARCHAR(50)")
    op.execute("UPDATE freelancers SET tier = 'new' WHERE tier IN ('FREE', 'Free', 'NEW', 'New')")
    op.execute("UPDATE freelancers SET tier = 'verified' WHERE tier IN ('BASIC', 'Basic', 'VERIFIED', 'Verified')")
    op.execute("UPDATE freelancers SET tier = 'toprated' WHERE tier IN ('PRO', 'Pro', 'TOPRATED', 'TopRated', 'top_rated')")
    
    # Deals table - status and payment_flow columns
    op.execute("ALTER TABLE deals ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE deals SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE deals SET status = 'active' WHERE status IN ('ACTIVE', 'Active')")
    op.execute("UPDATE deals SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS')")
    op.execute("UPDATE deals SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE deals SET status = 'disputed' WHERE status IN ('DISPUTED', 'Disputed')")
    op.execute("UPDATE deals SET status = 'cancelled' WHERE status IN ('CANCELLED', 'Cancelled')")
    
    op.execute("ALTER TABLE deals ALTER COLUMN payment_flow TYPE VARCHAR(50)")
    op.execute("UPDATE deals SET payment_flow = 'simplified' WHERE payment_flow IN ('SIMPLIFIED', 'Simplified')")
    op.execute("UPDATE deals SET payment_flow = 'full' WHERE payment_flow IN ('FULL', 'Full')")
    
    # Milestones table - status column
    op.execute("ALTER TABLE milestones ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE milestones SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE milestones SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS')")
    op.execute("UPDATE milestones SET status = 'submitted' WHERE status IN ('SUBMITTED', 'Submitted')")
    op.execute("UPDATE milestones SET status = 'approved' WHERE status IN ('APPROVED', 'Approved')")
    op.execute("UPDATE milestones SET status = 'rejected' WHERE status IN ('REJECTED', 'Rejected')")
    op.execute("UPDATE milestones SET status = 'paid' WHERE status IN ('PAID', 'Paid')")
    
    # Payments table - status column
    op.execute("ALTER TABLE payments ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE payments SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE payments SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')")
    op.execute("UPDATE payments SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE payments SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    op.execute("UPDATE payments SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')")
    
    # Transactions table - type and status columns
    op.execute("ALTER TABLE transactions ALTER COLUMN type TYPE VARCHAR(50)")
    op.execute("UPDATE transactions SET type = 'deposit' WHERE type IN ('DEPOSIT', 'Deposit')")
    op.execute("UPDATE transactions SET type = 'release' WHERE type IN ('RELEASE', 'Release')")
    op.execute("UPDATE transactions SET type = 'refund' WHERE type IN ('REFUND', 'Refund')")
    op.execute("UPDATE transactions SET type = 'commission' WHERE type IN ('COMMISSION', 'Commission')")
    
    op.execute("ALTER TABLE transactions ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE transactions SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE transactions SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')")
    op.execute("UPDATE transactions SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE transactions SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    op.execute("UPDATE transactions SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')")
    
    # Leads table - source and status columns
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE VARCHAR(50)")
    op.execute("UPDATE leads SET source = 'google' WHERE source IN ('GOOGLE', 'Google')")
    op.execute("UPDATE leads SET source = 'manual' WHERE source IN ('MANUAL', 'Manual')")
    op.execute("UPDATE leads SET source = 'referral' WHERE source IN ('REFERRAL', 'Referral')")
    op.execute("UPDATE leads SET source = 'import' WHERE source IN ('IMPORT', 'Import')")
    
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE leads SET status = 'new' WHERE status IN ('NEW', 'New')")
    op.execute("UPDATE leads SET status = 'assigned' WHERE status IN ('ASSIGNED', 'Assigned')")
    op.execute("UPDATE leads SET status = 'contacted' WHERE status IN ('CONTACTED', 'Contacted')")
    op.execute("UPDATE leads SET status = 'qualified' WHERE status IN ('QUALIFIED', 'Qualified')")
    op.execute("UPDATE leads SET status = 'converted' WHERE status IN ('CONVERTED', 'Converted')")
    op.execute("UPDATE leads SET status = 'lost' WHERE status IN ('LOST', 'Lost')")
    op.execute("UPDATE leads SET status = 'archived' WHERE status IN ('ARCHIVED', 'Archived')")
    
    # Lead_contacts table - status and consent_status columns
    op.execute("ALTER TABLE lead_contacts ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE lead_contacts SET status = 'contacted' WHERE status IN ('CONTACTED', 'Contacted')")
    op.execute("UPDATE lead_contacts SET status = 'interested' WHERE status IN ('INTERESTED', 'Interested')")
    op.execute("UPDATE lead_contacts SET status = 'negotiating' WHERE status IN ('NEGOTIATING', 'Negotiating')")
    op.execute("UPDATE lead_contacts SET status = 'closed' WHERE status IN ('CLOSED', 'Closed')")
    op.execute("UPDATE lead_contacts SET status = 'lost' WHERE status IN ('LOST', 'Lost')")
    op.execute("UPDATE lead_contacts SET status = 'cold' WHERE status IN ('COLD', 'Cold')")
    
    op.execute("ALTER TABLE lead_contacts ALTER COLUMN consent_status TYPE VARCHAR(50)")
    op.execute("UPDATE lead_contacts SET consent_status = 'contacted' WHERE consent_status IN ('CONTACTED', 'Contacted')")
    op.execute("UPDATE lead_contacts SET consent_status = 'vieweddemo' WHERE consent_status IN ('VIEWED_DEMO', 'ViewedDemo', 'VIEWEDDEMO')")
    op.execute("UPDATE lead_contacts SET consent_status = 'consented' WHERE consent_status IN ('CONSENTED', 'Consented')")
    op.execute("UPDATE lead_contacts SET consent_status = 'registered' WHERE consent_status IN ('REGISTERED', 'Registered')")
    op.execute("UPDATE lead_contacts SET consent_status = 'optedout' WHERE consent_status IN ('OPTED_OUT', 'OptedOut', 'OPTEDOUT')")
    
    # Outreach_messages table - channel and delivery_status columns
    op.execute("ALTER TABLE outreach_messages ALTER COLUMN channel TYPE VARCHAR(50)")
    op.execute("UPDATE outreach_messages SET channel = 'sms' WHERE channel IN ('SMS', 'Sms')")
    op.execute("UPDATE outreach_messages SET channel = 'email' WHERE channel IN ('EMAIL', 'Email')")
    op.execute("UPDATE outreach_messages SET channel = 'whatsapp' WHERE channel IN ('WHATSAPP', 'WhatsApp')")
    
    op.execute("ALTER TABLE outreach_messages ALTER COLUMN delivery_status TYPE VARCHAR(50)")
    op.execute("UPDATE outreach_messages SET delivery_status = 'sent' WHERE delivery_status IN ('SENT', 'Sent')")
    op.execute("UPDATE outreach_messages SET delivery_status = 'delivered' WHERE delivery_status IN ('DELIVERED', 'Delivered')")
    op.execute("UPDATE outreach_messages SET delivery_status = 'failed' WHERE delivery_status IN ('FAILED', 'Failed')")
    op.execute("UPDATE outreach_messages SET delivery_status = 'bounced' WHERE delivery_status IN ('BOUNCED', 'Bounced')")
    
    # Lead_activities table - activity_type column
    op.execute("ALTER TABLE lead_activities ALTER COLUMN activity_type TYPE VARCHAR(50)")
    op.execute("UPDATE lead_activities SET activity_type = 'followup' WHERE activity_type IN ('FOLLOW_UP', 'FollowUp', 'follow_up')")
    op.execute("UPDATE lead_activities SET activity_type = 'call' WHERE activity_type IN ('CALL', 'Call')")
    op.execute("UPDATE lead_activities SET activity_type = 'meeting' WHERE activity_type IN ('MEETING', 'Meeting')")
    op.execute("UPDATE lead_activities SET activity_type = 'email' WHERE activity_type IN ('EMAIL', 'Email')")
    op.execute("UPDATE lead_activities SET activity_type = 'note' WHERE activity_type IN ('NOTE', 'Note')")
    op.execute("UPDATE lead_activities SET activity_type = 'statuschange' WHERE activity_type IN ('STATUS_CHANGE', 'StatusChange', 'status_change')")
    
    # Business_insights table - freshness column
    op.execute("ALTER TABLE business_insights ALTER COLUMN freshness TYPE VARCHAR(50)")
    op.execute("UPDATE business_insights SET freshness = 'high' WHERE freshness IN ('HIGH', 'High')")
    op.execute("UPDATE business_insights SET freshness = 'medium' WHERE freshness IN ('MEDIUM', 'Medium')")
    op.execute("UPDATE business_insights SET freshness = 'low' WHERE freshness IN ('LOW', 'Low')")
    
    # Campaigns table - type and status columns
    op.execute("ALTER TABLE campaigns ALTER COLUMN type TYPE VARCHAR(50)")
    op.execute("UPDATE campaigns SET type = 'googlediscovery' WHERE type IN ('GOOGLE_DISCOVERY', 'GoogleDiscovery', 'google_discovery')")
    op.execute("UPDATE campaigns SET type = 'manualoutreach' WHERE type IN ('MANUAL_OUTREACH', 'ManualOutreach', 'manual_outreach')")
    op.execute("UPDATE campaigns SET type = 'referral' WHERE type IN ('REFERRAL', 'Referral')")
    op.execute("UPDATE campaigns SET type = 'retargeting' WHERE type IN ('RETARGETING', 'Retargeting')")
    
    op.execute("ALTER TABLE campaigns ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE campaigns SET status = 'draft' WHERE status IN ('DRAFT', 'Draft')")
    op.execute("UPDATE campaigns SET status = 'active' WHERE status IN ('ACTIVE', 'Active')")
    op.execute("UPDATE campaigns SET status = 'paused' WHERE status IN ('PAUSED', 'Paused')")
    op.execute("UPDATE campaigns SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')")
    op.execute("UPDATE campaigns SET status = 'archived' WHERE status IN ('ARCHIVED', 'Archived')")
    
    # Messages table - channel and status columns
    op.execute("ALTER TABLE messages ALTER COLUMN channel TYPE VARCHAR(50)")
    op.execute("UPDATE messages SET channel = 'inapp' WHERE channel IN ('IN_APP', 'InApp', 'INAPP')")
    op.execute("UPDATE messages SET channel = 'sms' WHERE channel IN ('SMS', 'Sms')")
    op.execute("UPDATE messages SET channel = 'email' WHERE channel IN ('EMAIL', 'Email')")
    op.execute("UPDATE messages SET channel = 'whatsapp' WHERE channel IN ('WHATSAPP', 'WhatsApp')")
    
    op.execute("ALTER TABLE messages ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE messages SET status = 'sent' WHERE status IN ('SENT', 'Sent')")
    op.execute("UPDATE messages SET status = 'delivered' WHERE status IN ('DELIVERED', 'Delivered')")
    op.execute("UPDATE messages SET status = 'read' WHERE status IN ('READ', 'Read')")
    op.execute("UPDATE messages SET status = 'failed' WHERE status IN ('FAILED', 'Failed')")
    
    # Update freelancer_roi table - period column
    op.execute("""
        UPDATE freelancer_roi 
        SET period = CASE
            WHEN period IN ('WEEK', 'Week') THEN 'week'
            WHEN period IN ('MONTH', 'Month') THEN 'month'
            WHEN period IN ('QUARTER', 'Quarter') THEN 'quarter'
            WHEN period IN ('ALL_TIME', 'AllTime', 'ALLTIME') THEN 'all_time'
            ELSE LOWER(period)
        END
    """)
    
    # Update kyc_documents table if exists - document_type and status columns
    op.execute("""
        UPDATE kyc_documents 
        SET document_type = CASE
            WHEN document_type IN ('AADHAAR', 'Aadhaar') THEN 'aadhaar'
            WHEN document_type IN ('PAN', 'Pan') THEN 'pan'
            WHEN document_type IN ('DRIVING_LICENSE', 'DrivingLicense') THEN 'driving_license'
            WHEN document_type IN ('PASSPORT', 'Passport') THEN 'passport'
            WHEN document_type IN ('BANK_ACCOUNT', 'BankAccount') THEN 'bank_account'
            ELSE LOWER(document_type)
        END
        WHERE document_type IS NOT NULL
    """)
    
    op.execute("""
        UPDATE kyc_documents 
        SET status = CASE
            WHEN status IN ('PENDING', 'Pending') THEN 'pending'
            WHEN status IN ('SUBMITTED', 'Submitted') THEN 'submitted'
            WHEN status IN ('UNDER_REVIEW', 'UnderReview') THEN 'under_review'
            WHEN status IN ('APPROVED', 'Approved') THEN 'approved'
            WHEN status IN ('REJECTED', 'Rejected') THEN 'rejected'
            ELSE LOWER(status)
        END
        WHERE status IS NOT NULL
    """)


def downgrade():
    """Revert enum values back to PascalCase/CamelCase."""
    
    # This is a one-way migration for simplicity
    # If you need to revert, you would need to implement the reverse logic
    pass

    
    # Freelancer_roi table - period column
    op.execute("ALTER TABLE freelancer_roi ALTER COLUMN period TYPE VARCHAR(50)")
    op.execute("UPDATE freelancer_roi SET period = 'week' WHERE period IN ('WEEK', 'Week')")
    op.execute("UPDATE freelancer_roi SET period = 'month' WHERE period IN ('MONTH', 'Month')")
    op.execute("UPDATE freelancer_roi SET period = 'quarter' WHERE period IN ('QUARTER', 'Quarter')")
    op.execute("UPDATE freelancer_roi SET period = 'alltime' WHERE period IN ('ALL_TIME', 'AllTime', 'ALLTIME', 'all_time')")
    
    # KYC_documents table - document_type and status columns
    op.execute("ALTER TABLE kyc_documents ALTER COLUMN document_type TYPE VARCHAR(50)")
    op.execute("UPDATE kyc_documents SET document_type = 'aadhaar' WHERE document_type IN ('AADHAAR', 'Aadhaar')")
    op.execute("UPDATE kyc_documents SET document_type = 'pan' WHERE document_type IN ('PAN', 'Pan')")
    op.execute("UPDATE kyc_documents SET document_type = 'drivinglicense' WHERE document_type IN ('DRIVING_LICENSE', 'DrivingLicense', 'driving_license')")
    op.execute("UPDATE kyc_documents SET document_type = 'passport' WHERE document_type IN ('PASSPORT', 'Passport')")
    op.execute("UPDATE kyc_documents SET document_type = 'bankaccount' WHERE document_type IN ('BANK_ACCOUNT', 'BankAccount', 'bank_account')")
    
    op.execute("ALTER TABLE kyc_documents ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE kyc_documents SET status = 'pending' WHERE status IN ('PENDING', 'Pending')")
    op.execute("UPDATE kyc_documents SET status = 'submitted' WHERE status IN ('SUBMITTED', 'Submitted')")
    op.execute("UPDATE kyc_documents SET status = 'underreview' WHERE status IN ('UNDER_REVIEW', 'UnderReview', 'under_review')")
    op.execute("UPDATE kyc_documents SET status = 'approved' WHERE status IN ('APPROVED', 'Approved')")
    op.execute("UPDATE kyc_documents SET status = 'rejected' WHERE status IN ('REJECTED', 'Rejected')")


def downgrade():
    """Revert enum values back to PascalCase/CamelCase."""
    
    # This is a one-way migration for simplicity
    # If you need to revert, you would need to implement the reverse logic
    pass
