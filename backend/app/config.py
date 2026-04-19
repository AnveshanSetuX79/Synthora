"""Application configuration management."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Authentication
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External APIs
    google_places_api_key: str = Field(..., alias="GOOGLE_PLACES_API_KEY")
    latlng_api_key: Optional[str] = Field(default=None, alias="LATLNG_API_KEY")
    use_latlng: bool = Field(default=False, alias="USE_LATLNG")
    
    # Payment Provider
    razorpay_key_id: Optional[str] = Field(default=None, alias="RAZORPAY_KEY_ID")
    razorpay_key_secret: Optional[str] = Field(default=None, alias="RAZORPAY_KEY_SECRET")
    
    # Communication Providers
    sms_provider_api_key: Optional[str] = Field(default=None, alias="SMS_PROVIDER_API_KEY")
    email_service_api_key: Optional[str] = Field(default=None, alias="EMAIL_SERVICE_API_KEY")
    whatsapp_business_api_key: Optional[str] = Field(default=None, alias="WHATSAPP_BUSINESS_API_KEY")
    
    # Application
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()
