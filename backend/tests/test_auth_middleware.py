"""Unit tests for JWT authentication middleware."""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.middleware.auth import (
    get_current_user,
    require_freelancer,
    require_business_owner,
    require_admin
)
from app.utils.auth import create_access_token


# Create a test app with protected routes
test_app = FastAPI()


@test_app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Protected route requiring authentication."""
    return {"message": "success", "user_id": current_user["user_id"]}


@test_app.get("/freelancer-only")
async def freelancer_route(current_user: dict = Depends(require_freelancer)):
    """Route requiring freelancer role."""
    return {"message": "freelancer access", "role": current_user["role"]}


@test_app.get("/business-only")
async def business_route(current_user: dict = Depends(require_business_owner)):
    """Route requiring business owner role."""
    return {"message": "business access", "role": current_user["role"]}


@test_app.get("/admin-only")
async def admin_route(current_user: dict = Depends(require_admin)):
    """Route requiring admin role."""
    return {"message": "admin access", "role": current_user["role"]}


@pytest.fixture
def middleware_client():
    """Create test client for middleware tests."""
    return TestClient(test_app)


class TestJWTMiddleware:
    """Test cases for JWT authentication middleware."""
    
    def test_protected_route_without_token(self, middleware_client):
        """Test accessing protected route without token fails."""
        response = middleware_client.get("/protected")
        
        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials
    
    def test_protected_route_with_valid_token(self, middleware_client):
        """Test accessing protected route with valid token succeeds."""
        # Create valid token
        token_data = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "role": "freelancer"
        }
        token = create_access_token(token_data)
        
        # Access protected route
        response = middleware_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "success"
        assert data["user_id"] == "test-user-123"
    
    def test_protected_route_with_invalid_token(self, middleware_client):
        """Test accessing protected route with invalid token fails."""
        response = middleware_client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_protected_route_with_malformed_header(self, middleware_client):
        """Test accessing protected route with malformed auth header fails."""
        response = middleware_client.get(
            "/protected",
            headers={"Authorization": "InvalidFormat token"}
        )
        
        assert response.status_code == 403
    
    def test_freelancer_route_with_freelancer_token(self, middleware_client):
        """Test freelancer-only route with freelancer token succeeds."""
        token_data = {
            "user_id": "freelancer-123",
            "email": "freelancer@example.com",
            "role": "freelancer",
            "tier": "New"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/freelancer-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "freelancer access"
        assert data["role"] == "freelancer"
    
    def test_freelancer_route_with_business_token(self, middleware_client):
        """Test freelancer-only route with business owner token fails."""
        token_data = {
            "user_id": "business-123",
            "email": "business@example.com",
            "role": "business_owner"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/freelancer-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()
    
    def test_business_route_with_business_token(self, middleware_client):
        """Test business-only route with business owner token succeeds."""
        token_data = {
            "user_id": "business-123",
            "email": "business@example.com",
            "role": "business_owner"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/business-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "business access"
        assert data["role"] == "business_owner"
    
    def test_business_route_with_freelancer_token(self, middleware_client):
        """Test business-only route with freelancer token fails."""
        token_data = {
            "user_id": "freelancer-123",
            "email": "freelancer@example.com",
            "role": "freelancer"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/business-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    def test_admin_route_with_admin_token(self, middleware_client):
        """Test admin-only route with admin token succeeds."""
        token_data = {
            "user_id": "admin-123",
            "email": "admin@example.com",
            "role": "admin"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "admin access"
        assert data["role"] == "admin"
    
    def test_admin_route_with_founder_token(self, middleware_client):
        """Test admin-only route with founder token succeeds."""
        token_data = {
            "user_id": "founder-123",
            "email": "founder@example.com",
            "role": "founder"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_admin_route_with_freelancer_token(self, middleware_client):
        """Test admin-only route with freelancer token fails."""
        token_data = {
            "user_id": "freelancer-123",
            "email": "freelancer@example.com",
            "role": "freelancer"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    def test_token_expiration_handling(self, middleware_client):
        """Test that expired tokens are rejected."""
        from datetime import timedelta
        
        # Create token with negative expiration (already expired)
        token_data = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "role": "freelancer"
        }
        token = create_access_token(token_data, expires_delta=timedelta(seconds=-1))
        
        response = middleware_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    def test_token_contains_all_user_data(self, middleware_client):
        """Test that middleware extracts all user data from token."""
        token_data = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "role": "freelancer",
            "tier": "Verified"
        }
        token = create_access_token(token_data)
        
        response = middleware_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        # The endpoint returns user_id, confirming middleware extracted it correctly
        assert response.json()["user_id"] == "test-user-123"
