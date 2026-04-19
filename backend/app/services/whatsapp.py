"""WhatsApp messaging service.

This service provides two modes:
1. MVP Mode: Generate wa.me links for manual sending (FREE, instant)
2. API Mode: WhatsApp Business API for automated sending (paid, requires setup)

MVP Mode is recommended for initial launch - it's free, instant, and has
10x better engagement than SMS.

Requirements: 6.1, 6.2, 36.1
"""
import logging
from typing import Optional, Dict
from urllib.parse import quote
import os

logger = logging.getLogger(__name__)


class WhatsAppError(Exception):
    """Base exception for WhatsApp errors."""
    pass


class WhatsAppService:
    """Service for WhatsApp messaging."""
    
    def __init__(self):
        """Initialize WhatsApp service."""
        # MVP mode uses wa.me links (free, manual)
        # API mode uses WhatsApp Business API (paid, automated)
        self.mode = os.getenv("WHATSAPP_MODE", "mvp")  # mvp or api
        
        # API mode credentials (optional)
        self.api_key = os.getenv("WHATSAPP_API_KEY")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
        self.api_enabled = self.mode == "api" and self.api_key is not None
        
        if self.mode == "mvp":
            logger.info("✅ WhatsApp MVP mode enabled (wa.me links)")
        elif self.api_enabled:
            logger.info("✅ WhatsApp API mode enabled")
        else:
            logger.warning("⚠️ WhatsApp API mode selected but credentials missing")
    
    def generate_whatsapp_link(
        self,
        phone: str,
        message: str,
        demo_url: Optional[str] = None
    ) -> str:
        """Generate WhatsApp wa.me link for manual sending.
        
        This is the MVP approach - generates a link that opens WhatsApp
        with pre-filled message. Freelancer just clicks "Send".
        
        Args:
            phone: Phone number (with country code, e.g., +919876543210)
            message: Message text
            demo_url: Optional demo URL to append
            
        Returns:
            WhatsApp wa.me link
            
        Example:
            https://wa.me/919876543210?text=Hi%20there!%20Check%20this%20demo
        """
        # Clean phone number (remove + and spaces)
        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        # Append demo URL if provided
        if demo_url:
            message = f"{message}\n\n🌐 View Demo: {demo_url}"
        
        # URL encode the message
        message_encoded = quote(message)
        
        # Generate wa.me link
        whatsapp_link = f"https://wa.me/{phone_clean}?text={message_encoded}"
        
        logger.info(f"📱 Generated WhatsApp link for {phone}")
        
        return whatsapp_link
    
    def send_message_mvp(
        self,
        phone: str,
        message: str,
        demo_url: Optional[str] = None
    ) -> Dict:
        """Send message via MVP mode (generates wa.me link).
        
        This returns a link that the freelancer can click to send the message.
        The link opens WhatsApp with pre-filled message.
        
        Args:
            phone: Phone number
            message: Message text
            demo_url: Optional demo URL
            
        Returns:
            Dictionary with whatsapp_link and instructions
        """
        whatsapp_link = self.generate_whatsapp_link(phone, message, demo_url)
        
        return {
            "status": "link_generated",
            "whatsapp_link": whatsapp_link,
            "phone": phone,
            "message": "Click the link to send via WhatsApp",
            "instructions": "Opens WhatsApp with pre-filled message. Just click Send!",
            "mode": "mvp"
        }
    
    def send_message_api(
        self,
        phone: str,
        message: str,
        demo_url: Optional[str] = None
    ) -> Dict:
        """Send message via WhatsApp Business API (automated).
        
        This requires WhatsApp Business API setup and costs money.
        Use this after MVP validation.
        
        Args:
            phone: Phone number
            message: Message text
            demo_url: Optional demo URL
            
        Returns:
            Dictionary with status and message_id
            
        Raises:
            WhatsAppError: If API sending fails
        """
        if not self.api_enabled:
            raise WhatsAppError(
                "WhatsApp API not configured. Set WHATSAPP_API_KEY and "
                "WHATSAPP_PHONE_NUMBER_ID in .env"
            )
        
        try:
            # Append demo URL if provided
            if demo_url:
                message = f"{message}\n\n🌐 View Demo: {demo_url}"
            
            # In production, use WhatsApp Business API
            # Example with Meta's Cloud API:
            # import requests
            # url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
            # headers = {
            #     "Authorization": f"Bearer {self.api_key}",
            #     "Content-Type": "application/json"
            # }
            # payload = {
            #     "messaging_product": "whatsapp",
            #     "to": phone.replace("+", ""),
            #     "type": "text",
            #     "text": {"body": message}
            # }
            # response = requests.post(url, json=payload, headers=headers)
            # response.raise_for_status()
            # result = response.json()
            # message_id = result["messages"][0]["id"]
            
            # Mock for development
            message_id = f"wamid_mock_{phone[-10:]}"
            logger.info(f"[MOCK] WhatsApp API message sent to {phone}")
            
            return {
                "status": "sent",
                "message_id": message_id,
                "phone": phone,
                "mode": "api"
            }
            
        except Exception as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            raise WhatsAppError(f"Failed to send WhatsApp message: {str(e)}")
    
    def send_message(
        self,
        phone: str,
        message: str,
        demo_url: Optional[str] = None
    ) -> Dict:
        """Send WhatsApp message (auto-detects mode).
        
        Args:
            phone: Phone number
            message: Message text
            demo_url: Optional demo URL
            
        Returns:
            Dictionary with status and details
        """
        if self.mode == "mvp":
            return self.send_message_mvp(phone, message, demo_url)
        else:
            return self.send_message_api(phone, message, demo_url)
    
    def create_demo_message(
        self,
        business_name: str,
        freelancer_name: str,
        demo_url: str,
        business_category: Optional[str] = None
    ) -> str:
        """Create formatted demo message for WhatsApp.
        
        Args:
            business_name: Name of the business
            freelancer_name: Name of the freelancer
            demo_url: Demo website URL
            business_category: Optional business category
            
        Returns:
            Formatted message text
        """
        category_text = f" ({business_category})" if business_category else ""
        
        message = f"""Hi {business_name}! 👋

I'm {freelancer_name}, a web developer. I noticed your business{category_text} doesn't have a website yet.

I've created a FREE demo website for you to see how it could look! 🌐

✨ Check it out: {demo_url}

Would you like to discuss bringing your business online? I'd love to help you grow! 🚀

Reply here if interested!"""
        
        return message
    
    def create_follow_up_message(
        self,
        business_name: str,
        freelancer_name: str,
        demo_url: str
    ) -> str:
        """Create follow-up message.
        
        Args:
            business_name: Name of the business
            freelancer_name: Name of the freelancer
            demo_url: Demo website URL
            
        Returns:
            Formatted follow-up message
        """
        message = f"""Hi {business_name}! 👋

Just following up on the demo website I shared earlier.

🌐 Demo Link: {demo_url}

Have you had a chance to check it out? I'd love to hear your thoughts and discuss how a professional website can help grow your business! 📈

Let me know if you have any questions!

- {freelancer_name}"""
        
        return message
    
    def get_delivery_status(self, message_id: str) -> str:
        """Get delivery status of WhatsApp message.
        
        Args:
            message_id: Message ID from send_message
            
        Returns:
            Status string: sent, delivered, read, failed
        """
        if self.mode == "mvp":
            # MVP mode doesn't track delivery (manual sending)
            return "manual"
        
        if not self.api_enabled:
            return "unknown"
        
        try:
            # In production, query WhatsApp API for status
            # import requests
            # url = f"https://graph.facebook.com/v17.0/{message_id}"
            # headers = {"Authorization": f"Bearer {self.api_key}"}
            # response = requests.get(url, headers=headers)
            # result = response.json()
            # return result.get("status", "unknown")
            
            # Mock for development
            return "delivered"
            
        except Exception as e:
            logger.error(f"Error getting WhatsApp status: {str(e)}")
            return "unknown"


# Message templates
class WhatsAppTemplates:
    """Pre-defined WhatsApp message templates."""
    
    FIRST_CONTACT = """Hi {business_name}! 👋

I'm {freelancer_name}, a web developer. I noticed your business doesn't have a website yet.

I've created a FREE demo website for you! 🌐

✨ Check it out: {demo_url}

Would you like to discuss bringing your business online? 🚀"""
    
    FOLLOW_UP = """Hi {business_name}! 👋

Following up on the demo website I shared.

🌐 Demo: {demo_url}

Have you had a chance to check it out? Let me know if you have any questions!

- {freelancer_name}"""
    
    DEAL_PROPOSAL = """Hi {business_name}! 👋

I'd love to build a professional website for your business! 💼

📦 Package: {package_name}
💰 Price: ₹{amount}
⏱️ Timeline: {timeline}

Interested? Let's discuss! 🚀"""
