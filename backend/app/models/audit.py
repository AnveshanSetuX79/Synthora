"""Audit logging for data changes."""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class AuditLog(Base):
    """Audit trail for all data changes."""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(String(36), nullable=False, index=True)
    action = Column(String(20), nullable=False, index=True)  # INSERT, UPDATE, DELETE
    
    # Change tracking
    old_data = Column(JSON, nullable=True)  # Previous state
    new_data = Column(JSON, nullable=True)  # New state
    changed_fields = Column(JSON, nullable=True)  # List of changed field names
    
    # User tracking
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_role = Column(String(50), nullable=True)
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User")
