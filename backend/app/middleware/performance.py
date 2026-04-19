"""Performance monitoring middleware."""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance and log slow requests."""
    
    # Performance thresholds (in seconds)
    SLOW_REQUEST_THRESHOLD = 1.0  # Log warning if request takes > 1 second
    CRITICAL_THRESHOLD = 3.0  # Log error if request takes > 3 seconds
    
    # Target response times (Requirement 13.3)
    TARGET_TIMES = {
        '/api/leads/map': 2.0,  # Map load: 2 seconds (1000 pins)
        '/api/leads/search': 1.0,  # Search results: 1 second
        '/api/demos/': 1.0,  # Demo retrieval: 1 second
        '/api/messages': 0.5,  # Chat messages: 500ms
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track performance."""
        # Start timer
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")
            raise
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add performance header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log performance
        self._log_performance(request, response, process_time)
        
        return response
    
    def _log_performance(self, request: Request, response: Response, process_time: float):
        """Log request performance based on thresholds."""
        path = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Skip logging for successful fast requests to reduce overhead
        if process_time < self.SLOW_REQUEST_THRESHOLD and status_code == 200:
            return
        
        # Check if path matches any target endpoint
        target_time = None
        for target_path, target_threshold in self.TARGET_TIMES.items():
            if path.startswith(target_path):
                target_time = target_threshold
                break
        
        # Determine log level based on performance
        if process_time >= self.CRITICAL_THRESHOLD:
            logger.error(
                f"CRITICAL SLOW REQUEST: {method} {path} "
                f"took {process_time:.4f}s (threshold: {self.CRITICAL_THRESHOLD}s) "
                f"[Status: {status_code}]"
            )
        elif process_time >= self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Slow request: {method} {path} "
                f"took {process_time:.4f}s (threshold: {self.SLOW_REQUEST_THRESHOLD}s) "
                f"[Status: {status_code}]"
            )
        elif target_time and process_time > target_time:
            logger.warning(
                f"Target exceeded: {method} {path} "
                f"took {process_time:.4f}s (target: {target_time}s) "
                f"[Status: {status_code}]"
            )
        
        # Store metrics for monitoring (could be sent to monitoring service)
        self._record_metric(path, method, process_time, status_code)
    
    def _record_metric(self, path: str, method: str, process_time: float, status_code: int):
        """Record metric for monitoring dashboard.
        
        In production, this could send metrics to:
        - Prometheus
        - DataDog
        - New Relic
        - CloudWatch
        etc.
        """
        # For now, just log at debug level
        # In production, implement actual metrics collection
        pass


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests for debugging and monitoring."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details."""
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"[Status: {response.status_code}]"
        )
        
        return response
