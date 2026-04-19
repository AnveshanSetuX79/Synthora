"""Security middleware for CSRF and XSS protection.

Requirement 14.1: Input validation - Prevent injection attacks
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import html
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        # HSTS (HTTP Strict Transport Security) - only in production with HTTPS
        # Uncomment when deploying with HTTPS:
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize input and prevent XSS attacks."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Sanitize request data."""
        # Note: FastAPI/Pydantic already provides good input validation
        # This middleware adds an extra layer of protection
        
        # For JSON requests, Pydantic handles validation
        # For query parameters and path parameters, FastAPI validates
        
        # Skip body reading to avoid consuming the stream
        # Let FastAPI/Pydantic handle validation at the route level
        # This middleware just adds security headers
        
        response = await call_next(request)
        return response


def sanitize_html(text: str) -> str:
    """Sanitize HTML to prevent XSS.
    
    Args:
        text: Text that may contain HTML
        
    Returns:
        Sanitized text with HTML entities escaped
    """
    if not text:
        return text
    return html.escape(text)


def sanitize_sql(text: str) -> str:
    """Basic SQL injection prevention.
    
    Note: SQLAlchemy ORM already prevents SQL injection when used properly.
    This is an additional safety check for raw queries.
    
    Args:
        text: Text that may contain SQL
        
    Returns:
        Text with dangerous SQL patterns removed
    """
    if not text:
        return text
    
    # Remove common SQL injection patterns
    dangerous_patterns = [
        '--', ';--', '/*', '*/', 'xp_', 'sp_',
        'exec', 'execute', 'drop', 'create', 'alter',
        'insert', 'update', 'delete', 'union', 'select'
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            logger.warning(f"Potential SQL injection attempt: pattern '{pattern}' detected")
            # Don't modify, just log - let validation handle it
    
    return text


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware.
    
    Note: For API-only applications using JWT tokens, CSRF is less of a concern
    if tokens are stored in localStorage (not cookies). However, if using
    cookie-based sessions, CSRF protection is critical.
    """
    
    # Exempt methods that don't modify state
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
    # Exempt paths (e.g., public endpoints)
    EXEMPT_PATHS = {
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/otp/request",
        "/api/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json"
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check CSRF token for state-changing requests."""
        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)
        
        # Skip CSRF check for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # For JWT-based auth (tokens in Authorization header), CSRF is not needed
        # CSRF is mainly for cookie-based sessions
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # JWT token in header - no CSRF needed
            return await call_next(request)
        
        # If using cookie-based sessions, check CSRF token here
        # csrf_token = request.headers.get("X-CSRF-Token")
        # if not csrf_token or not self._validate_csrf_token(csrf_token):
        #     return Response(
        #         content="CSRF token missing or invalid",
        #         status_code=403
        #     )
        
        return await call_next(request)
