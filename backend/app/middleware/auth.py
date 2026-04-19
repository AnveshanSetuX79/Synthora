"""JWT authentication middleware."""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime

from ..utils.auth import decode_access_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    Usage:
        @router.get("/protected")
        async def protected_route(
            current_user: dict = Depends(get_current_user)
        ):
            user_id = current_user["user_id"]
            role = current_user["role"]
            ...
    
    Returns:
        User information from token payload
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode and verify token
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token expiration
    exp = payload.get("exp")
    if exp and datetime.utcnow().timestamp() > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def require_freelancer(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require freelancer role.
    
    Usage:
        @router.get("/freelancer-only")
        async def freelancer_route(
            current_user: dict = Depends(require_freelancer)
        ):
            ...
    
    Returns:
        User information if role is freelancer
        
    Raises:
        HTTPException: If user role is not freelancer
    """
    user_role = current_user.get("role")
    if user_role != "freelancer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Required role: freelancer"
        )
    
    return current_user


async def require_business_owner(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require business owner role.
    
    Usage:
        @router.get("/business-only")
        async def business_route(
            current_user: dict = Depends(require_business_owner)
        ):
            ...
    
    Returns:
        User information if role is businessowner
        
    Raises:
        HTTPException: If user role is not businessowner
    """
    user_role = current_user.get("role")
    if user_role != "businessowner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: businessowner, got: {user_role}"
        )
    
    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require admin or founder role.
    
    Usage:
        @router.get("/admin-only")
        async def admin_route(
            current_user: dict = Depends(require_admin)
        ):
            ...
    
    Returns:
        User information if role is admin or founder
        
    Raises:
        HTTPException: If user role is not admin or founder
    """
    user_role = current_user.get("role")
    if user_role not in ["admin", "founder"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: admin, founder"
        )
    
    return current_user
