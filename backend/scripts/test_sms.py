#!/usr/bin/env python3
"""
Test SMS integration.

This script tests SMS sending functionality to verify your SMS provider
is configured correctly.

Usage:
    python scripts/test_sms.py +919876543210
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.sms import SMSService, SMSError


def test_sms(phone_number: str):
    """Test SMS sending to a phone number."""
    print(f"🧪 Testing SMS Integration")
    print(f"=" * 50)
    
    # Initialize SMS service
    sms_service = SMSService()
    
    print(f"\n📋 Configuration:")
    print(f"  Enabled: {sms_service.enabled}")
    print(f"  Provider: {sms_service.provider}")
    print(f"  Sender ID: {sms_service.sender_id}")
    print(f"  API Key: {'✅ Set' if sms_service.api_key else '❌ Not Set'}")
    
    if not sms_service.enabled:
        print(f"\n⚠️  SMS is DISABLED")
        print(f"   Set SMS_ENABLED=true in .env to enable")
        return
    
    if not sms_service.api_key:
        print(f"\n❌ SMS API key not configured!")
        print(f"   Set SMS_API_KEY in .env")
        return
    
    # Test message
    message = (
        f"Hi! This is a test message from LocalAI Leads platform. "
        f"Your SMS integration is working correctly! 🎉"
    )
    
    print(f"\n📱 Sending test SMS to {phone_number}...")
    print(f"   Message: {message[:50]}...")
    
    try:
        result = sms_service.send_sms(phone_number, message)
        
        print(f"\n✅ SMS sent successfully!")
        print(f"   Status: {result['status']}")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Provider: {result['provider']}")
        
        print(f"\n📊 Next Steps:")
        print(f"   1. Check your phone for the SMS")
        print(f"   2. Verify the message content")
        print(f"   3. If not received, check provider dashboard")
        
        # Check delivery status
        print(f"\n🔍 Checking delivery status...")
        status = sms_service.get_delivery_status(result['message_id'])
        print(f"   Delivery Status: {status}")
        
    except SMSError as e:
        print(f"\n❌ SMS sending failed!")
        print(f"   Error: {str(e)}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Verify API credentials in .env")
        print(f"   2. Check account balance")
        print(f"   3. Verify phone number format (+91 for India)")
        print(f"   4. Check provider dashboard for errors")
    except Exception as e:
        print(f"\n❌ Unexpected error!")
        print(f"   Error: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_sms.py <phone_number>")
        print("Example: python scripts/test_sms.py +919876543210")
        sys.exit(1)
    
    phone = sys.argv[1]
    test_sms(phone)
