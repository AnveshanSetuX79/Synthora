"""Global API rate limiting middleware.

Requirement 14.1: Rate limiting - API abuse prevention
"""
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        """Initialize rate limiter.
        
        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage: {ip: [(timestamp, count), ...]}
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
        
        # Exempt paths from rate limiting
        self.exempt_paths = {
            "/api/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits before processing request."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limits
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request.
        
        Handles X-Forwarded-For header for proxied requests.
        """
        # Check X-Forwarded-For header (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limits.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if within limits, False if exceeded
        """
        now = datetime.now()
        
        # Clean old entries (older than 1 hour)
        self._clean_old_entries(client_ip, now)
        
        # Check minute limit
        minute_ago = now - timedelta(minutes=1)
        minute_count = sum(
            1 for timestamp in self.minute_requests[client_ip]
            if timestamp > minute_ago
        )
        
        if minute_count >= self.requests_per_minute:
            return False
        
        # Check hour limit
        hour_ago = now - timedelta(hours=1)
        hour_count = sum(
            1 for timestamp in self.hour_requests[client_ip]
            if timestamp > hour_ago
        )
        
        if hour_count >= self.requests_per_hour:
            return False
        
        # Record this request
        self.minute_requests[client_ip].append(now)
        self.hour_requests[client_ip].append(now)
        
        return True
    
    def _clean_old_entries(self, client_ip: str, now: datetime):
        """Remove old entries to prevent memory bloat."""
        # Clean minute entries
        minute_ago = now - timedelta(minutes=1)
        self.minute_requests[client_ip] = [
            ts for ts in self.minute_requests[client_ip]
            if ts > minute_ago
        ]
        
        # Clean hour entries
        hour_ago = now - timedelta(hours=1)
        self.hour_requests[client_ip] = [
            ts for ts in self.hour_requests[client_ip]
            if ts > hour_ago
        ]
        
        # Remove empty entries
        if not self.minute_requests[client_ip]:
            del self.minute_requests[client_ip]
        if not self.hour_requests[client_ip]:
            del self.hour_requests[client_ip]


# For production with Redis:
"""
from redis import Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# In main.py startup:
@app.on_event("startup")
async def startup():
    redis = Redis(host="localhost", port=6379, decode_responses=True)
    await FastAPILimiter.init(redis)

# In routes:
@router.get("/endpoint", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def endpoint():
    pass
"""
