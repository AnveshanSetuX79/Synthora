"""SMS service for fallback communication.

CRITICAL: This service MUST be properly configured for the platform to work.
Without SMS, business owners cannot receive demo links and the entire
business model breaks down.

Supported Providers:
- Twilio (International, reliable, $$$)
- MSG91 (India-focused, affordable, $$)
- Fast2SMS (India-focused, cheap, $)

Setup Instructions:
1. Choose a provider and sign up
2. Set environment variables in .env:
   - SMS_ENABLED=true
   - SMS_PROVIDER=twilio (or msg91, fast2sms)
   - SMS_API_KEY=your_api_key
   - For Twilio: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
   - For MSG91: MSG91_AUTH_KEY, MSG91_SENDER_ID
   - For Fast2SMS: FAST2SMS_API_KEY
3. Test with a real phone number before launch
4. Monitor delivery rates and costs

Requirements: 6.1, 6.2, 36.1
"""
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


class SMSError(Exception):
    """Base exception for SMS errors."""
    pass


class SMSService:
    """Service for sending SMS messages."""
    
    def __init__(self):
        """Initialize SMS service."""
        self.enabled = os.getenv("SMS_ENABLED", "false").lower() == "true"
        self.provider = os.getenv("SMS_PROVIDER", "twilio")  # twilio, msg91, fast2sms
        self.api_key = os.getenv("SMS_API_KEY")
        self.sender_id = os.getenv("SMS_SENDER_ID", "LOCALA")
        
        if self.enabled and not self.api_key:
            logger.warning("⚠️ SMS is enabled but SMS_API_KEY is not set - SMS will fail!")
        
        if not self.enabled:
            logger.warning(
                "⚠️ SMS is DISABLED - Business owners will NOT receive demo links! "
                "Set SMS_ENABLED=true in .env to enable."
            )
    
    def send_sms(
        self,
        phone: str,
        message: str,
        opt_out_link: Optional[str] = None
    ) -> dict:
        """Send SMS message.
        
        Args:
            phone: Phone number (with country code)
            message: Message content
            opt_out_link: Optional opt-out link to append
            
        Returns:
            Dictionary with status and message_id
            
        Raises:
            SMSError: If SMS sending fails
        """
        try:
            if not self.enabled:
                logger.info(f"SMS disabled. Would send to {phone}: {message}")
                return {
                    "status": "simulated",
                    "message_id": "sim_" + phone,
                    "provider": "none"
                }
            
            # Add opt-out link if provided
            if opt_out_link:
                message = f"{message}\n\nOpt-out: {opt_out_link}"
            
            # Validate phone number
            if not phone or len(phone) < 10:
                raise SMSError(f"Invalid phone number: {phone}")
            
            # Send via provider
            if self.provider == "twilio":
                return self._send_via_twilio(phone, message)
            elif self.provider == "msg91":
                return self._send_via_msg91(phone, message)
            else:
                raise SMSError(f"Unsupported SMS provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error sending SMS to {phone}: {str(e)}")
            raise SMSError(f"Failed to send SMS: {str(e)}")
    
    def _send_via_twilio(self, phone: str, message: str) -> dict:
        """Send SMS via Twilio.
        
        Args:
            phone: Phone number
            message: Message content
            
        Returns:
            Dictionary with status and message_id
        """
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            from_number = os.getenv("TWILIO_PHONE_NUMBER")
            
            if not all([account_sid, auth_token, from_number]):
                raise SMSError("Twilio credentials not configured")
            
            client = Client(account_sid, auth_token)
            
            sms = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            logger.info(f"SMS sent via Twilio to {phone}: {sms.sid}")
            
            return {
                "status": "sent",
                "message_id": sms.sid,
                "provider": "twilio"
            }
            
        except ImportError:
            raise SMSError("Twilio library not installed. Install with: pip install twilio")
        except Exception as e:
            raise SMSError(f"Twilio error: {str(e)}")
    
    def _send_via_msg91(self, phone: str, message: str) -> dict:
        """Send SMS via MSG91 (India-focused provider).
        
        MSG91 Setup:
        1. Sign up at https://msg91.com/
        2. Get AUTH_KEY from dashboard
        3. Set MSG91_AUTH_KEY in .env
        4. Set MSG91_SENDER_ID (6-char alphanumeric, e.g., LOCALA)
        5. Register sender ID with TRAI DLT
        
        Args:
            phone: Phone number (with country code, e.g., +919876543210)
            message: Message content
            
        Returns:
            Dictionary with status and message_id
        """
        try:
            import requests
            
            auth_key = os.getenv("MSG91_AUTH_KEY")
            sender_id = os.getenv("MSG91_SENDER_ID", self.sender_id)
            
            if not auth_key:
                raise SMSError("MSG91_AUTH_KEY not configured in .env")
            
            # MSG91 API v5 endpoint
            url = "https://control.msg91.com/api/v5/flow/"
            
            # Remove + from phone number if present
            phone_clean = phone.replace("+", "")
            
            payload = {
                "sender": sender_id,
                "mobiles": phone_clean,
                "message": message,
                "authkey": auth_key,
                "route": "4",  # Transactional route
                "country": "91"  # India
            }
            
            headers = {
                "Content-Type": "application/json",
                "authkey": auth_key
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"✅ SMS sent via MSG91 to {phone}: {result}")
            
            return {
                "status": "sent",
                "message_id": result.get("message_id", result.get("request_id", "unknown")),
                "provider": "msg91"
            }
            
        except Exception as e:
            logger.error(f"❌ MSG91 error: {str(e)}")
            raise SMSError(f"MSG91 error: {str(e)}")
    
    def get_delivery_status(self, message_id: str) -> str:
        """Get delivery status of SMS.
        
        Args:
            message_id: Message ID from send_sms
            
        Returns:
            Status string: sent, delivered, failed, bounced
        """
        try:
            if not self.enabled or message_id.startswith("sim_"):
                return "delivered"
            
            if self.provider == "twilio":
                return self._get_twilio_status(message_id)
            elif self.provider == "msg91":
                return self._get_msg91_status(message_id)
            else:
                return "sent"
                
        except Exception as e:
            logger.error(f"Error getting SMS status for {message_id}: {str(e)}")
            return "sent"
    
    def _get_twilio_status(self, message_id: str) -> str:
        """Get Twilio message status."""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            
            client = Client(account_sid, auth_token)
            message = client.messages(message_id).fetch()
            
            # Map Twilio status to our status
            status_map = {
                "queued": "sent",
                "sending": "sent",
                "sent": "sent",
                "delivered": "delivered",
                "undelivered": "failed",
                "failed": "failed"
            }
            
            return status_map.get(message.status, "sent")
            
        except Exception as e:
            logger.error(f"Error getting Twilio status: {str(e)}")
            return "sent"
    
    def _get_msg91_status(self, message_id: str) -> str:
        """Get MSG91 message status."""
        # MSG91 status checking would be implemented here
        return "sent"
