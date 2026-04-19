"""Email service for outreach communication."""
import os
import logging
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        """Initialize email service."""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@localaileads.com")
        self.from_name = os.getenv("FROM_NAME", "LocalAI Leads")
        
        self.enabled = bool(self.smtp_user and self.smtp_password)
        
        if not self.enabled:
            logger.warning("Email service not configured. Set SMTP_USER and SMTP_PASSWORD.")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> dict:
        """Send email message.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            Dict with success status and message_id
            
        Raises:
            Exception: If email sending fails
        """
        if not self.enabled:
            logger.info(f"[MOCK] Email to {to_email}: {subject}")
            return {
                "success": True,
                "message_id": "mock_email_id",
                "provider": "mock"
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach text and HTML parts
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            
            return {
                "success": True,
                "message_id": msg['Message-ID'],
                "provider": "smtp"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
    
    def send_outreach_email(
        self,
        to_email: str,
        business_name: str,
        freelancer_name: str,
        demo_url: Optional[str] = None,
        message: Optional[str] = None,
        opt_out_link: Optional[str] = None
    ) -> dict:
        """Send outreach email to business.
        
        Args:
            to_email: Business email
            business_name: Name of the business
            freelancer_name: Name of the freelancer
            demo_url: Optional demo website URL
            message: Optional custom message
            opt_out_link: Optional opt-out link
            
        Returns:
            Dict with success status
        """
        subject = f"Free Website Preview for {business_name}"
        
        # Plain text version
        body_text = f"""Hi {business_name}!

{message or f"I'm {freelancer_name}, a web developer helping local businesses establish their online presence."}

"""
        
        if demo_url:
            body_text += f"""I've created a free demo website for your business. Check it out here:
{demo_url}

"""
        
        body_text += f"""This is just a preview to show what's possible. If you're interested in taking your business online, I'd love to help!

Best regards,
{freelancer_name}
LocalAI Leads Platform

"""
        
        if opt_out_link:
            body_text += f"\nTo unsubscribe from future messages: {opt_out_link}"
        
        # HTML version
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9fafb; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Free Website Preview</h1>
        </div>
        <div class="content">
            <p>Hi {business_name}!</p>
            <p>{message or f"I'm {freelancer_name}, a web developer helping local businesses establish their online presence."}</p>
"""
        
        if demo_url:
            body_html += f"""
            <p>I've created a free demo website for your business:</p>
            <p style="text-align: center;">
                <a href="{demo_url}" class="button">View Your Demo Website</a>
            </p>
"""
        
        body_html += f"""
            <p>This is just a preview to show what's possible. If you're interested in taking your business online, I'd love to help!</p>
            <p>Best regards,<br>{freelancer_name}<br>LocalAI Leads Platform</p>
        </div>
        <div class="footer">
"""
        
        if opt_out_link:
            body_html += f'<p><a href="{opt_out_link}">Unsubscribe from future messages</a></p>'
        
        body_html += """
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, body_text, body_html)
    
    def send_notification_email(
        self,
        to_email: str,
        recipient_name: str,
        notification_type: str,
        **kwargs
    ) -> dict:
        """Send notification email.
        
        Args:
            to_email: Recipient email
            recipient_name: Recipient name
            notification_type: Type of notification
            **kwargs: Additional template variables
            
        Returns:
            Dict with success status
        """
        templates = {
            'new_message': {
                'subject': f"New message from {kwargs.get('sender_name', 'someone')}",
                'text': f"""Hi {recipient_name},

You have a new message from {kwargs.get('sender_name', 'someone')}:

"{kwargs.get('message_preview', '')}"

View the full conversation:
{kwargs.get('link', '')}

Best regards,
LocalAI Leads Team
""",
                'html': f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2563eb; color: white; padding: 20px; text-align: center;">
            <h1>New Message</h1>
        </div>
        <div style="padding: 20px; background: #f9fafb;">
            <p>Hi {recipient_name},</p>
            <p>You have a new message from <strong>{kwargs.get('sender_name', 'someone')}</strong>:</p>
            <div style="background: white; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
                <p style="font-style: italic;">"{kwargs.get('message_preview', '')}"</p>
            </div>
            <p style="text-align: center;">
                <a href="{kwargs.get('link', '')}" style="display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px;">View Conversation</a>
            </p>
        </div>
        <div style="padding: 20px; text-align: center; font-size: 12px; color: #666;">
            <p>LocalAI Leads Platform</p>
        </div>
    </div>
</body>
</html>
"""
            },
            'milestone_submitted': {
                'subject': f"Milestone submitted for review - {kwargs.get('deal_title', '')}",
                'text': f"""Hi {recipient_name},

{kwargs.get('freelancer_name', 'A freelancer')} has submitted a milestone for your review:

Deal: {kwargs.get('deal_title', '')}
Milestone: {kwargs.get('milestone_title', '')}

Please review and approve or request changes:
{kwargs.get('link', '')}

Best regards,
LocalAI Leads Team
""",
                'html': f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2563eb; color: white; padding: 20px; text-align: center;">
            <h1>Milestone Submitted</h1>
        </div>
        <div style="padding: 20px; background: #f9fafb;">
            <p>Hi {recipient_name},</p>
            <p><strong>{kwargs.get('freelancer_name', 'A freelancer')}</strong> has submitted a milestone for your review:</p>
            <div style="background: white; padding: 15px; margin: 20px 0;">
                <p><strong>Deal:</strong> {kwargs.get('deal_title', '')}</p>
                <p><strong>Milestone:</strong> {kwargs.get('milestone_title', '')}</p>
            </div>
            <p style="text-align: center;">
                <a href="{kwargs.get('link', '')}" style="display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px;">Review Milestone</a>
            </p>
        </div>
        <div style="padding: 20px; text-align: center; font-size: 12px; color: #666;">
            <p>LocalAI Leads Platform</p>
        </div>
    </div>
</body>
</html>
"""
            },
            'payment_processed': {
                'subject': f"Payment processed - ₹{kwargs.get('amount', 0):.2f}",
                'text': f"""Hi {recipient_name},

Your payment has been processed successfully!

Amount: ₹{kwargs.get('amount', 0):.2f}
Deal: {kwargs.get('deal_title', '')}

View payment details:
{kwargs.get('link', '')}

Best regards,
LocalAI Leads Team
""",
                'html': f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #10b981; color: white; padding: 20px; text-align: center;">
            <h1>Payment Processed</h1>
        </div>
        <div style="padding: 20px; background: #f9fafb;">
            <p>Hi {recipient_name},</p>
            <p>Your payment has been processed successfully!</p>
            <div style="background: white; padding: 15px; margin: 20px 0;">
                <p><strong>Amount:</strong> ₹{kwargs.get('amount', 0):.2f}</p>
                <p><strong>Deal:</strong> {kwargs.get('deal_title', '')}</p>
            </div>
            <p style="text-align: center;">
                <a href="{kwargs.get('link', '')}" style="display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 6px;">View Details</a>
            </p>
        </div>
        <div style="padding: 20px; text-align: center; font-size: 12px; color: #666;">
            <p>LocalAI Leads Platform</p>
        </div>
    </div>
</body>
</html>
"""
            }
        }
        
        template = templates.get(notification_type)
        if not template:
            logger.error(f"Unknown notification type: {notification_type}")
            return {"success": False, "error": "Unknown notification type"}
        
        return self.send_email(
            to_email=to_email,
            subject=template['subject'],
            body_text=template['text'],
            body_html=template['html']
        )
