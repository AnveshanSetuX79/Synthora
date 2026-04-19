"""TRAI DLT (Distributed Ledger Technology) integration service.

Requirement 14.3: TRAI regulations - SMS/email outreach compliance

IMPORTANT: This is a template implementation. You must:
1. Register with a DLT platform (Vodafone, Airtel, Jio, BSNL, etc.)
2. Register your business entity
3. Register message templates
4. Get template IDs and entity IDs
5. Update the configuration with your actual credentials
"""
import requests
import logging
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TRAIDLTError(Exception):
    """Base exception for TRAI DLT errors."""
    pass


class TemplateNotFoundError(TRAIDLTError):
    """Raised when message template is not registered."""
    pass


class TRAIDLTService:
    """Service for TRAI DLT compliance.
    
    TRAI DLT is mandatory for commercial SMS in India.
    All promotional and transactional SMS must be sent through registered templates.
    """
    
    def __init__(self):
        """Initialize TRAI DLT service."""
        # DLT Platform credentials (get from your DLT provider)
        self.entity_id = os.getenv("TRAI_ENTITY_ID", "")  # Your registered entity ID
        self.api_key = os.getenv("TRAI_DLT_API_KEY", "")
        self.api_url = os.getenv("TRAI_DLT_API_URL", "")
        
        # Registered message templates
        # Format: {template_name: {template_id, template_text, variables}}
        self.templates = {
            "lead_notification": {
                "template_id": os.getenv("TRAI_TEMPLATE_LEAD_NOTIFICATION", ""),
                "template_text": "Hi {name}, new lead available: {business_name} in {location}. Login to view details. -LocalAI",
                "variables": ["name", "business_name", "location"],
                "category": "transactional"
            },
            "otp_verification": {
                "template_id": os.getenv("TRAI_TEMPLATE_OTP", ""),
                "template_text": "Your OTP for LocalAI is {otp}. Valid for 10 minutes. Do not share. -LocalAI",
                "variables": ["otp"],
                "category": "transactional"
            },
            "deal_update": {
                "template_id": os.getenv("TRAI_TEMPLATE_DEAL_UPDATE", ""),
                "template_text": "Deal update: {business_name} - {status}. Check your dashboard for details. -LocalAI",
                "variables": ["business_name", "status"],
                "category": "transactional"
            },
            "payment_reminder": {
                "template_id": os.getenv("TRAI_TEMPLATE_PAYMENT", ""),
                "template_text": "Payment of Rs.{amount} pending for {business_name}. Complete payment to proceed. -LocalAI",
                "variables": ["amount", "business_name"],
                "category": "transactional"
            }
        }
        
        # Check if DLT is configured
        self.is_configured = bool(self.entity_id and self.api_key)
        
        if not self.is_configured:
            logger.warning(
                "TRAI DLT not configured. SMS sending will fail in production. "
                "Set TRAI_ENTITY_ID and TRAI_DLT_API_KEY in .env"
            )
    
    def get_template(self, template_name: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """Get DLT template with variables filled.
        
        Args:
            template_name: Name of registered template
            variables: Dictionary of variable values
            
        Returns:
            Dictionary with template_id and formatted message
            
        Raises:
            TemplateNotFoundError: If template not registered
            TRAIDLTError: If variables don't match template
        """
        if template_name not in self.templates:
            raise TemplateNotFoundError(
                f"Template '{template_name}' not found. "
                f"Available templates: {list(self.templates.keys())}"
            )
        
        template = self.templates[template_name]
        
        # Check if template is registered
        if not template["template_id"]:
            raise TRAIDLTError(
                f"Template '{template_name}' not registered with DLT. "
                f"Register template and update TRAI_TEMPLATE_{template_name.upper()} in .env"
            )
        
        # Validate variables
        required_vars = set(template["variables"])
        provided_vars = set(variables.keys())
        
        if required_vars != provided_vars:
            missing = required_vars - provided_vars
            extra = provided_vars - required_vars
            error_msg = []
            if missing:
                error_msg.append(f"Missing variables: {missing}")
            if extra:
                error_msg.append(f"Extra variables: {extra}")
            raise TRAIDLTError(". ".join(error_msg))
        
        # Format message with variables
        try:
            message = template["template_text"].format(**variables)
        except KeyError as e:
            raise TRAIDLTError(f"Error formatting template: {str(e)}")
        
        return {
            "template_id": template["template_id"],
            "entity_id": self.entity_id,
            "message": message,
            "category": template["category"]
        }
    
    def validate_message(self, message: str, template_name: str) -> bool:
        """Validate that message matches registered template.
        
        Args:
            message: Message to validate
            template_name: Template name to validate against
            
        Returns:
            True if message matches template structure
        """
        if template_name not in self.templates:
            return False
        
        template = self.templates[template_name]
        template_text = template["template_text"]
        
        # Basic validation: check if message structure matches
        # In production, implement more sophisticated matching
        # considering variable substitutions
        
        return True  # Simplified for now
    
    def register_template(
        self,
        template_name: str,
        template_text: str,
        category: str,
        variables: list
    ) -> str:
        """Register a new template with DLT platform.
        
        This is typically done through the DLT platform's web interface,
        not programmatically. This method is for documentation purposes.
        
        Args:
            template_name: Name for the template
            template_text: Template text with {variable} placeholders
            category: 'transactional' or 'promotional'
            variables: List of variable names
            
        Returns:
            Template ID from DLT platform
        """
        logger.info(
            f"To register template '{template_name}':\n"
            f"1. Login to your DLT platform (Vodafone/Airtel/Jio/BSNL)\n"
            f"2. Navigate to Template Registration\n"
            f"3. Submit template:\n"
            f"   Text: {template_text}\n"
            f"   Category: {category}\n"
            f"   Variables: {variables}\n"
            f"4. Wait for approval (usually 24-48 hours)\n"
            f"5. Update .env with: TRAI_TEMPLATE_{template_name.upper()}=<template_id>"
        )
        
        raise NotImplementedError(
            "Template registration must be done through DLT platform web interface"
        )
    
    def check_dlt_status(self) -> Dict[str, Any]:
        """Check DLT configuration status.
        
        Returns:
            Dictionary with configuration status
        """
        status = {
            "configured": self.is_configured,
            "entity_id": self.entity_id if self.entity_id else "NOT_SET",
            "templates": {}
        }
        
        for name, template in self.templates.items():
            status["templates"][name] = {
                "registered": bool(template["template_id"]),
                "template_id": template["template_id"] if template["template_id"] else "NOT_SET",
                "category": template["category"]
            }
        
        return status


# Singleton instance
_trai_dlt_service = None


def get_trai_dlt_service() -> TRAIDLTService:
    """Get TRAI DLT service instance."""
    global _trai_dlt_service
    if _trai_dlt_service is None:
        _trai_dlt_service = TRAIDLTService()
    return _trai_dlt_service
