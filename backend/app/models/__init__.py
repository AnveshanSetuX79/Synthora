"""SQLAlchemy models for LocalAI Leads Platform."""
from .user import User, Freelancer, BusinessOwner, Admin
from .business import Business, BusinessInsight
from .lead import Lead, LeadContact, LeadActivity, OutreachMessage
from .demo import DemoWebsite
from .deal import Deal, Milestone
from .payment import Payment, Transaction
from .message import Message, Conversation
from .analytics import AnalyticsEvent, FreelancerROI, ConversionIntelligence
from .campaign import Campaign, MessageTemplate
from .audit import AuditLog
from .kyc import KYCDocument

__all__ = [
    "User",
    "Freelancer",
    "BusinessOwner",
    "Admin",
    "Business",
    "BusinessInsight",
    "Lead",
    "LeadContact",
    "LeadActivity",
    "OutreachMessage",
    "DemoWebsite",
    "Deal",
    "Milestone",
    "Payment",
    "Transaction",
    "Message",
    "Conversation",
    "AnalyticsEvent",
    "FreelancerROI",
    "ConversionIntelligence",
    "Campaign",
    "MessageTemplate",
    "AuditLog",
    "KYCDocument",
]
