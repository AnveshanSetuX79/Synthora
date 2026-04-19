"""Unit tests for OTP verification and login APIs."""
import pytest
from fastapi.testclient import TestClient

from app.models.user import User
from app.utils.otp import store_otp, generate_otp


class TestOTPVerification:
    """Test cases for POST /api/auth/verify-otp endpoint."""
    
    def test_verify_otp_success(self, client, db_session):
        """Test successful OTP verification."""
        # First register a user
        register_payload = {
            "email": "otp@example.com",
            "phone": "+919876543230",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "OTP Test User"
        }
        
        register_response = client.post("/api/auth/register", json=register_payload)
        assert register_response.status_code == 201
        
        # Get the OTP from storage (in production, user would receive via SMS)
        from app.utils.otp import get_otp
        otp = get_otp(register_payload["phone"])
        assert otp is not None
        
        # Verify OTP
        verify_payload = {
            "phone": register_payload["phone"],
            "otp_code": otp
        }
        
        response = client.post("/api/auth/verify-otp", json=verify_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response
        assert data["phone_verified"] is True
        assert "access_token" in data
        
        # Verify database update
        user = db_session.query(User).filter(User.email == register_payload["email"]).first()
        assert user.phone_verified is True
        assert user.is_active is True
    
    def test_verify_otp_invalid_code(self, client, db_session):
        """Test OTP verification with invalid code."""
        # Register a user
        register_payload = {
            "email": "invalid_otp@example.com",
            "phone": "+919876543231",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Invalid OTP User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        # Try to verify with wrong OTP
        verify_payload = {
            "phone": register_payload["phone"],
            "otp_code": "000000"
        }
        
        response = client.post("/api/auth/verify-otp", json=verify_payload)
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_verify_otp_nonexistent_phone(self, client):
        """Test OTP verification with non-existent phone number."""
        verify_payload = {
            "phone": "+919999999999",
            "otp_code": "123456"
        }
        
        response = client.post("/api/auth/verify-otp", json=verify_payload)
        
        assert response.status_code == 400 or response.status_code == 404
    
    def test_verify_otp_invalid_format(self, client):
        """Test OTP verification with invalid OTP format."""
        verify_payload = {
            "phone": "+919876543232",
            "otp_code": "12345"  # Only 5 digits
        }
        
        response = client.post("/api/auth/verify-otp", json=verify_payload)
        
        assert response.status_code == 422


class TestLogin:
    """Test cases for POST /api/auth/login endpoint."""
    
    def test_login_with_email_success(self, client, db_session):
        """Test successful login with email."""
        # Register and verify a user
        register_payload = {
            "email": "login@example.com",
            "phone": "+919876543240",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Login Test User"
        }
        
        register_response = client.post("/api/auth/register", json=register_payload)
        assert register_response.status_code == 201
        
        # Verify OTP to activate account
        from app.utils.otp import get_otp
        otp = get_otp(register_payload["phone"])
        client.post("/api/auth/verify-otp", json={
            "phone": register_payload["phone"],
            "otp_code": otp
        })
        
        # Login with email
        login_payload = {
            "identifier": register_payload["email"],
            "password": register_payload["password"]
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == register_payload["email"]
        assert data["role"] == "freelancer"
        assert data["phone_verified"] is True
    
    def test_login_with_phone_success(self, client, db_session):
        """Test successful login with phone number."""
        # Register and verify a user
        register_payload = {
            "email": "phone_login@example.com",
            "phone": "+919876543241",
            "password": "SecurePass123",
            "role": "business_owner",
            "owner_name": "Phone Login User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        # Verify OTP
        from app.utils.otp import get_otp
        otp = get_otp(register_payload["phone"])
        client.post("/api/auth/verify-otp", json={
            "phone": register_payload["phone"],
            "otp_code": otp
        })
        
        # Login with phone
        login_payload = {
            "identifier": register_payload["phone"],
            "password": register_payload["password"]
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["role"] == "business_owner"
    
    def test_login_wrong_password(self, client, db_session):
        """Test login with incorrect password."""
        # Register a user
        register_payload = {
            "email": "wrong_pass@example.com",
            "phone": "+919876543242",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Wrong Pass User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        # Try to login with wrong password
        login_payload = {
            "identifier": register_payload["email"],
            "password": "WrongPassword123"
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_payload = {
            "identifier": "nonexistent@example.com",
            "password": "SecurePass123"
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        
        assert response.status_code == 400
    
    def test_login_unverified_account(self, client, db_session):
        """Test login with unverified account fails."""
        # Register but don't verify
        register_payload = {
            "email": "unverified@example.com",
            "phone": "+919876543243",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Unverified User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        # Try to login without verifying OTP
        login_payload = {
            "identifier": register_payload["email"],
            "password": register_payload["password"]
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        
        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
    
    def test_login_jwt_token_valid(self, client, db_session):
        """Test that login returns valid JWT token."""
        from app.utils.auth import decode_access_token
        
        # Register and verify
        register_payload = {
            "email": "jwt_login@example.com",
            "phone": "+919876543244",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "JWT Login User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        from app.utils.otp import get_otp
        otp = get_otp(register_payload["phone"])
        client.post("/api/auth/verify-otp", json={
            "phone": register_payload["phone"],
            "otp_code": otp
        })
        
        # Login
        login_payload = {
            "identifier": register_payload["email"],
            "password": register_payload["password"]
        }
        
        response = client.post("/api/auth/login", json=login_payload)
        data = response.json()
        token = data["access_token"]
        
        # Decode and verify token
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["email"] == register_payload["email"]
        assert decoded["role"] == "freelancer"
        assert "user_id" in decoded
        assert "exp" in decoded
    
    def test_login_updates_last_active(self, client, db_session):
        """Test that login updates last_active timestamp."""
        # Register and verify
        register_payload = {
            "email": "last_active@example.com",
            "phone": "+919876543245",
            "password": "SecurePass123",
            "role": "freelancer",
            "name": "Last Active User"
        }
        
        client.post("/api/auth/register", json=register_payload)
        
        from app.utils.otp import get_otp
        otp = get_otp(register_payload["phone"])
        client.post("/api/auth/verify-otp", json={
            "phone": register_payload["phone"],
            "otp_code": otp
        })
        
        # Get user before login
        user_before = db_session.query(User).filter(User.email == register_payload["email"]).first()
        last_active_before = user_before.last_active
        
        # Login
        login_payload = {
            "identifier": register_payload["email"],
            "password": register_payload["password"]
        }
        
        client.post("/api/auth/login", json=login_payload)
        
        # Check last_active was updated
        db_session.expire(user_before)
        user_after = db_session.query(User).filter(User.email == register_payload["email"]).first()
        
        assert user_after.last_active is not None
        if last_active_before:
            assert user_after.last_active > last_active_before
