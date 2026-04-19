"""NDNC (National Do Not Call) Registry integration service.

Requirement 14.3: NDNC registry - Do Not Call compliance

IMPORTANT: This is a template implementation. You must:
1. Register with TRAI NDNC registry
2. Get API credentials
3. Implement actual NDNC checking before sending SMS
"""
import requests
import logging
from typing import Optional, Set
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class NDNCError(Exception):
    """Base exception for NDNC errors."""
    pass


class NDNCService:
    """Service for NDNC (Do Not Call) registry compliance.
    
    Before sending promotional SMS in India, you must check if the number
    is registered in the NDNC registry. Transactional SMS are exempt.
    """
    
    def __init__(self):
        """Initialize NDNC service."""
        # NDNC API credentials (get from TRAI)
        self.api_key = os.getenv("NDNC_API_KEY", "")
        self.api_url = os.getenv("NDNC_API_URL", "https://www.nccptrai.gov.in/nccpregistry")
        
        # Local opt-out list (users who opted out through our platform)
        self.local_optouts: Set[str] = set()
        
        # Cache for NDNC checks (to reduce API calls)
        self.ndnc_cache: dict = {}  # {phone: (is_registered, timestamp)}
        self.cache_duration = timedelta(days=7)  # Cache for 7 days
        
        self.is_configured = bool(self.api_key)
        
        if not self.is_configured:
            logger.warning(
                "NDNC not configured. Set NDNC_API_KEY in .env. "
                "SMS to DND numbers will be blocked in production."
            )
    
    def check_dnd_status(self, phone_number: str, message_type: str = "promotional") -> bool:
        """Check if phone number is registered in DND/NDNC.
        
        Args:
            phone_number: Phone number to check (10 digits)
            message_type: 'promotional' or 'transactional'
            
        Returns:
            True if SMS can be sent, False if number is in DND
        """
        # Normalize phone number
        phone = self._normalize_phone(phone_number)
        
        # Transactional messages are exempt from NDNC
        if message_type == "transactional":
            logger.debug(f"Transactional SMS to {phone} - NDNC check skipped")
            return True
        
        # Check local opt-out list first
        if phone in self.local_optouts:
            logger.info(f"Phone {phone} in local opt-out list")
            return False
        
        # Check cache
        if phone in self.ndnc_cache:
            is_dnd, timestamp = self.ndnc_cache[phone]
            if datetime.now() - timestamp < self.cache_duration:
                logger.debug(f"Using cached NDNC status for {phone}: {is_dnd}")
                return not is_dnd
        
        # Check NDNC registry
        try:
            is_dnd = self._check_ndnc_registry(phone)
            
            # Cache the result
            self.ndnc_cache[phone] = (is_dnd, datetime.now())
            
            if is_dnd:
                logger.info(f"Phone {phone} is registered in NDNC/DND")
                return False
            else:
                logger.debug(f"Phone {phone} not in NDNC/DND")
                return True
                
        except Exception as e:
            logger.error(f"Error checking NDNC for {phone}: {str(e)}")
            # In case of error, allow the SMS (fail open)
            # In production, you might want to fail closed (block SMS)
            return True
    
    def _check_ndnc_registry(self, phone: str) -> bool:
        """Check NDNC registry via API.
        
        Args:
            phone: Normalized phone number
            
        Returns:
            True if number is in DND, False otherwise
        """
        if not self.is_configured:
            logger.warning("NDNC API not configured - skipping check")
            return False
        
        # TODO: Implement actual NDNC API call
        # This is a placeholder - actual implementation depends on TRAI API
        
        """
        Example API call (actual API may differ):
        
        response = requests.post(
            f"{self.api_url}/check",
            json={"phone": phone},
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("is_dnd", False)
        else:
            raise NDNCError(f"NDNC API error: {response.status_code}")
        """
        
        # For now, return False (not in DND)
        # Update this when you have NDNC API access
        return False
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to 10 digits.
        
        Args:
            phone: Phone number in any format
            
        Returns:
            10-digit phone number
        """
        # Remove all non-digit characters
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Remove country code if present
        if digits.startswith('91') and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith('+91') and len(digits) == 13:
            digits = digits[3:]
        
        # Validate length
        if len(digits) != 10:
            raise ValueError(f"Invalid phone number: {phone}")
        
        return digits
    
    def add_to_optout(self, phone_number: str):
        """Add phone number to local opt-out list.
        
        Args:
            phone_number: Phone number to add
        """
        phone = self._normalize_phone(phone_number)
        self.local_optouts.add(phone)
        logger.info(f"Added {phone} to local opt-out list")
        
        # TODO: Store in database for persistence
        # For now, using in-memory set
    
    def remove_from_optout(self, phone_number: str):
        """Remove phone number from local opt-out list.
        
        Args:
            phone_number: Phone number to remove
        """
        phone = self._normalize_phone(phone_number)
        if phone in self.local_optouts:
            self.local_optouts.remove(phone)
            logger.info(f"Removed {phone} from local opt-out list")
    
    def is_opted_out(self, phone_number: str) -> bool:
        """Check if phone number is in local opt-out list.
        
        Args:
            phone_number: Phone number to check
            
        Returns:
            True if opted out, False otherwise
        """
        phone = self._normalize_phone(phone_number)
        return phone in self.local_optouts
    
    def get_optout_count(self) -> int:
        """Get count of opted-out numbers.
        
        Returns:
            Number of opted-out phone numbers
        """
        return len(self.local_optouts)
    
    def clear_cache(self):
        """Clear NDNC cache."""
        self.ndnc_cache.clear()
        logger.info("NDNC cache cleared")


# Singleton instance
_ndnc_service = None


def get_ndnc_service() -> NDNCService:
    """Get NDNC service instance."""
    global _ndnc_service
    if _ndnc_service is None:
        _ndnc_service = NDNCService()
    return _ndnc_service
