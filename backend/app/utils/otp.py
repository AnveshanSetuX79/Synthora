"""OTP generation and management utilities."""
import random
from typing import Dict, Optional
from datetime import datetime, timedelta

# TODO: Replace with Redis for production
# In-memory OTP storage for MVP
otp_storage: Dict[str, Dict[str, any]] = {}

OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def store_otp(phone: str, otp: str) -> None:
    """
    Store OTP temporarily.
    
    TODO: Replace with Redis for production to support multiple instances
    and proper expiration handling.
    """
    otp_storage[phone] = {
        "otp": otp,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    }


def verify_otp(phone: str, otp: str) -> bool:
    """
    Verify OTP for a phone number.
    
    Returns:
        True if OTP is valid and not expired, False otherwise
    """
    print(f"[OTP Verify] Checking OTP for phone: {phone}")
    print(f"[OTP Verify] Provided OTP: {otp}")
    print(f"[OTP Verify] Stored OTPs: {list(otp_storage.keys())}")
    
    if phone not in otp_storage:
        print(f"[OTP Verify] Phone not found in storage")
        return False
    
    stored_data = otp_storage[phone]
    print(f"[OTP Verify] Stored OTP: {stored_data['otp']}")
    
    # Check if OTP has expired
    if datetime.utcnow() > stored_data["expires_at"]:
        print(f"[OTP Verify] OTP expired")
        del otp_storage[phone]
        return False
    
    # Verify OTP
    if stored_data["otp"] == otp:
        print(f"[OTP Verify] OTP matched! Removing from storage")
        # Remove OTP after successful verification
        del otp_storage[phone]
        return True
    
    print(f"[OTP Verify] OTP mismatch")
    return False


def get_otp(phone: str) -> Optional[str]:
    """
    Get stored OTP for a phone number (for testing/debugging).
    
    Returns:
        OTP string if exists and not expired, None otherwise
    """
    if phone not in otp_storage:
        return None
    
    stored_data = otp_storage[phone]
    
    # Check if OTP has expired
    if datetime.utcnow() > stored_data["expires_at"]:
        del otp_storage[phone]
        return None
    
    return stored_data["otp"]


async def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Send OTP via SMS.
    
    TODO: Integrate with real SMS provider (TRAI-compliant).
    For MVP, this is a mock implementation.
    
    Args:
        phone: Phone number to send OTP to
        otp: OTP code to send
    
    Returns:
        True if SMS sent successfully, False otherwise
    """
    # Mock implementation - just log the OTP
    print(f"[SMS Mock] Sending OTP {otp} to {phone}")
    
    # TODO: Implement real SMS provider integration
    # Example with a generic SMS provider:
    # try:
    #     sms_client = SMSProvider(api_key=os.getenv("SMS_PROVIDER_API_KEY"))
    #     response = await sms_client.send(
    #         to=phone,
    #         message=f"Your LocalAI Leads verification code is: {otp}. Valid for 10 minutes."
    #     )
    #     return response.success
    # except Exception as e:
    #     print(f"SMS sending failed: {e}")
    #     return False
    
    return True
