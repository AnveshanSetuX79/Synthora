"""Unit tests for user registration API."""
import pytest
from fastapi.testclient import TestClient

from app.models.user import User, Freelancer, BusinessOwner


class TestUserRegistration:
    """Test cases for POST /api/auth/register endpoint."""
    
    def test_register_freelancer_success(self, client, db_session):
        """Test successful freelancer registration."""
        payload = {
            "email": "freelancer@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "John Doe",
            "portfolio_url": "https://johndoe.dev"
        }
        
        response = client.post("/api/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "user_id" in data
        assert data["email"] == payload["email"]
        assert data["role"] == "freelancer"
        assert data["phone"] == payload["phone"]
        assert data["phone_verified"] is False
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["freelancer_id"] is not None
        assert data["tier"] == "New"
        
        # Verify database records
        user = db_session.query(User).filter(User.email == payload["email"]).first()
        assert user is not None
        assert user.role.value == "freelancer"
        
        freelancer = db_session.query(Freelancer).filter(Freelancer.user_id == user.id).first()
        assert freelancer is not None
        assert freelancer.name == payload["name"]
        assert freelancer.tier.value == "New"
        assert freelancer.daily_limit == 3
    
    def test_register_business_owner_success(self, client, db_session):
        """Test successful business owner registration."""
        payload = {
            "email": "owner@restaurant.com",
            "phone": "+919876543211",
            "password": "SecurePass123",
            "role": "business_owner",
            "owner_name": "Jane Smith",
            "business_name": "Jane's Restaurant"
        }
        
        response = client.post("/api/auth/register", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "user_id" in data
        assert data["email"] == payload["email"]
        assert data["role"] == "business_owner"
        assert data["phone"] == payload["phone"]
        assert "access_token" in data
        assert data["business_owner_id"] is not None
        
        # Verify database records
        user = db_session.query(User).filter(User.email == payload["email"]).first()
        assert user is not None
        assert user.role.value == "business_owner"
        
        business_owner = db_session.query(BusinessOwner).filter(BusinessOwner.user_id == user.id).first()
        assert business_owner is not None
        assert business_owner.owner_name == payload["owner_name"]
    
    def test_register_duplicate_email(self, client, db_session):
        """Test registration with duplicate email fails."""
        payload = {
            "email": "duplicate@example.com",
            "phone": "+919876543212",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "First User"
        }
        
        # First registration should succeed
        response1 = client.post("/api/auth/register", json=payload)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        payload["phone"] = "+919876543213"
        payload["name"] = "Second User"
        response2 = client.post("/api/auth/register", json=payload)
        
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        payload = {
            "email": "invalid-email",
            "phone": "+919876543214",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_weak_password(self, client):
        """Test registration with weak password fails."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543215",
            "password": "weak",
            "role": "freelancer",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_password_without_uppercase(self, client):
        """Test password validation requires uppercase letter."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543216",
            "password": "lowercase123",
            "role": "freelancer",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_password_without_number(self, client):
        """Test password validation requires number."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543217",
            "password": "NoNumbers",
            "role": "freelancer",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_invalid_role(self, client):
        """Test registration with invalid role fails."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543218",
            "password": "SecurePass123",
            "role": "invalid_role",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_freelancer_without_name(self, client):
        """Test freelancer registration without name fails."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543219",
            "password": "SecurePass123",
            "role": "freelancer"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_business_owner_without_owner_name(self, client):
        """Test business owner registration without owner_name fails."""
        payload = {
            "email": "test@example.com",
            "phone": "+919876543220",
            "password": "SecurePass123",
            "role": "business_owner"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_register_invalid_phone_format(self, client):
        """Test registration with invalid phone format fails."""
        payload = {
            "email": "test@example.com",
            "phone": "123",  # Too short
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422
    
    def test_jwt_token_contains_user_data(self, client):
        """Test that JWT token contains correct user data."""
        from app.utils.auth import decode_access_token
        
        payload = {
            "email": "jwt@example.com",
            "phone": "+919876543221",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "JWT Test User"
        }
        
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        token = data["access_token"]
        
        # Decode and verify token
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["email"] == payload["email"]
        assert decoded["role"] == "freelancer"
        assert decoded["tier"] == "New"
        assert "user_id" in decoded
        assert "exp" in decoded
