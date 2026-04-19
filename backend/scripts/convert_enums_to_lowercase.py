"""Script to convert all enum values to lowercase in the database."""
import sys
sys.path.append('.')

from app.database import engine
from sqlalchemy import text

def convert_enums():
    """Convert all enum columns to VARCHAR and update values to lowercase."""
    
    with engine.begin() as conn:
        print("Converting enum values to lowercase...")
        
        # Users table
        print("- users.role")
        conn.execute(text("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE users SET role = 'freelancer' WHERE role IN ('FREELANCER', 'Freelancer')"))
        conn.execute(text("UPDATE users SET role = 'businessowner' WHERE role IN ('BUSINESS_OWNER', 'BusinessOwner', 'business_owner')"))
        conn.execute(text("UPDATE users SET role = 'admin' WHERE role IN ('ADMIN', 'Admin')"))
        conn.execute(text("UPDATE users SET role = 'founder' WHERE role IN ('FOUNDER', 'Founder')"))
        
        # Freelancers table
        print("- freelancers.tier")
        conn.execute(text("ALTER TABLE freelancers ALTER COLUMN tier TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE freelancers SET tier = 'new' WHERE tier IN ('FREE', 'Free', 'NEW', 'New')"))
        conn.execute(text("UPDATE freelancers SET tier = 'verified' WHERE tier IN ('BASIC', 'Basic', 'VERIFIED', 'Verified')"))
        conn.execute(text("UPDATE freelancers SET tier = 'toprated' WHERE tier IN ('PRO', 'Pro', 'TOPRATED', 'TopRated', 'top_rated')"))
        
        # Deals table
        print("- deals.status, deals.payment_flow")
        conn.execute(text("ALTER TABLE deals ALTER COLUMN status TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE deals SET status = 'pending' WHERE status IN ('PENDING', 'Pending')"))
        conn.execute(text("UPDATE deals SET status = 'active' WHERE status IN ('ACTIVE', 'Active')"))
        conn.execute(text("UPDATE deals SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS', 'in_progress')"))
        conn.execute(text("UPDATE deals SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')"))
        conn.execute(text("UPDATE deals SET status = 'disputed' WHERE status IN ('DISPUTED', 'Disputed')"))
        conn.execute(text("UPDATE deals SET status = 'cancelled' WHERE status IN ('CANCELLED', 'Cancelled')"))
        
        conn.execute(text("ALTER TABLE deals ALTER COLUMN payment_flow TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE deals SET payment_flow = 'simplified' WHERE payment_flow IN ('SIMPLIFIED', 'Simplified')"))
        conn.execute(text("UPDATE deals SET payment_flow = 'full' WHERE payment_flow IN ('FULL', 'Full')"))
        
        # Milestones table
        print("- milestones.status")
        conn.execute(text("ALTER TABLE milestones ALTER COLUMN status TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE milestones SET status = 'pending' WHERE status IN ('PENDING', 'Pending')"))
        conn.execute(text("UPDATE milestones SET status = 'inprogress' WHERE status IN ('IN_PROGRESS', 'InProgress', 'INPROGRESS', 'in_progress')"))
        conn.execute(text("UPDATE milestones SET status = 'submitted' WHERE status IN ('SUBMITTED', 'Submitted')"))
        conn.execute(text("UPDATE milestones SET status = 'approved' WHERE status IN ('APPROVED', 'Approved')"))
        conn.execute(text("UPDATE milestones SET status = 'rejected' WHERE status IN ('REJECTED', 'Rejected')"))
        conn.execute(text("UPDATE milestones SET status = 'paid' WHERE status IN ('PAID', 'Paid')"))
        
        # Payments table
        print("- payments.status")
        conn.execute(text("ALTER TABLE payments ALTER COLUMN status TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE payments SET status = 'pending' WHERE status IN ('PENDING', 'Pending')"))
        conn.execute(text("UPDATE payments SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')"))
        conn.execute(text("UPDATE payments SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')"))
        conn.execute(text("UPDATE payments SET status = 'failed' WHERE status IN ('FAILED', 'Failed')"))
        conn.execute(text("UPDATE payments SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')"))
        
        # Transactions table
        print("- transactions.type, transactions.status")
        conn.execute(text("ALTER TABLE transactions ALTER COLUMN type TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE transactions SET type = 'deposit' WHERE type IN ('DEPOSIT', 'Deposit')"))
        conn.execute(text("UPDATE transactions SET type = 'release' WHERE type IN ('RELEASE', 'Release')"))
        conn.execute(text("UPDATE transactions SET type = 'refund' WHERE type IN ('REFUND', 'Refund')"))
        conn.execute(text("UPDATE transactions SET type = 'commission' WHERE type IN ('COMMISSION', 'Commission')"))
        
        conn.execute(text("ALTER TABLE transactions ALTER COLUMN status TYPE VARCHAR(50)"))
        conn.execute(text("UPDATE transactions SET status = 'pending' WHERE status IN ('PENDING', 'Pending')"))
        conn.execute(text("UPDATE transactions SET status = 'processing' WHERE status IN ('PROCESSING', 'Processing')"))
        conn.execute(text("UPDATE transactions SET status = 'completed' WHERE status IN ('COMPLETED', 'Completed')"))
        conn.execute(text("UPDATE transactions SET status = 'failed' WHERE status IN ('FAILED', 'Failed')"))
        conn.execute(text("UPDATE transactions SET status = 'refunded' WHERE status IN ('REFUNDED', 'Refunded')"))
        
        # Update alembic version
        print("- Updating alembic version to 004")
        conn.execute(text("UPDATE alembic_version SET version_num = '004' WHERE version_num = '003'"))
        
        print("\n✅ All enum values converted to lowercase successfully!")

if __name__ == "__main__":
    convert_enums()


def convert_remaining_enums():
    """Convert any remaining enum columns that were missed."""
    
    with engine.begin() as conn:
        print("\nConverting remaining enum columns...")
        
        # Freelancer_roi table - period column (if not already done)
        try:
            print("- freelancer_roi.period")
            conn.execute(text("ALTER TABLE freelancer_roi ALTER COLUMN period TYPE VARCHAR(50)"))
            conn.execute(text("UPDATE freelancer_roi SET period = 'week' WHERE period IN ('WEEK', 'Week')"))
            conn.execute(text("UPDATE freelancer_roi SET period = 'month' WHERE period IN ('MONTH', 'Month')"))
            conn.execute(text("UPDATE freelancer_roi SET period = 'quarter' WHERE period IN ('QUARTER', 'Quarter')"))
            conn.execute(text("UPDATE freelancer_roi SET period = 'alltime' WHERE period IN ('ALL_TIME', 'AllTime', 'ALLTIME', 'all_time')"))
        except Exception as e:
            print(f"  Skipped (already converted or doesn't exist): {e}")
        
        # Analytics_events table - event_type column
        try:
            print("- analytics_events.event_type")
            conn.execute(text("ALTER TABLE analytics_events ALTER COLUMN event_type TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Leads table - source and status columns
        try:
            print("- leads.source, leads.status")
            conn.execute(text("ALTER TABLE leads ALTER COLUMN source TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE leads ALTER COLUMN status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Lead_contacts table - status and consent_status columns
        try:
            print("- lead_contacts.status, lead_contacts.consent_status")
            conn.execute(text("ALTER TABLE lead_contacts ALTER COLUMN status TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE lead_contacts ALTER COLUMN consent_status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Outreach_messages table - channel and delivery_status columns
        try:
            print("- outreach_messages.channel, outreach_messages.delivery_status")
            conn.execute(text("ALTER TABLE outreach_messages ALTER COLUMN channel TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE outreach_messages ALTER COLUMN delivery_status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Lead_activities table - activity_type column
        try:
            print("- lead_activities.activity_type")
            conn.execute(text("ALTER TABLE lead_activities ALTER COLUMN activity_type TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Messages table - channel and status columns
        try:
            print("- messages.channel, messages.status")
            conn.execute(text("ALTER TABLE messages ALTER COLUMN channel TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE messages ALTER COLUMN status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Campaigns table - type and status columns
        try:
            print("- campaigns.type, campaigns.status")
            conn.execute(text("ALTER TABLE campaigns ALTER COLUMN type TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE campaigns ALTER COLUMN status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # Business_insights table - freshness column
        try:
            print("- business_insights.freshness")
            conn.execute(text("ALTER TABLE business_insights ALTER COLUMN freshness TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        # KYC_documents table - document_type and status columns
        try:
            print("- kyc_documents.document_type, kyc_documents.status")
            conn.execute(text("ALTER TABLE kyc_documents ALTER COLUMN document_type TYPE VARCHAR(50)"))
            conn.execute(text("ALTER TABLE kyc_documents ALTER COLUMN status TYPE VARCHAR(50)"))
        except Exception as e:
            print(f"  Skipped: {e}")
        
        print("\n✅ All remaining enum columns converted to VARCHAR(50)!")

if __name__ == "__main__":
    convert_enums()
    convert_remaining_enums()
