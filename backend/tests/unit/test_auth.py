"""
Unit tests for authentication endpoints and JWT functionality.
Tests registration, login, token refresh, and user info endpoints.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.auth.jwt_handler import create_access_token, verify_token
from src.api.auth.password import hash_password, verify_password


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hashing(self):
        """Test that password hashing works correctly."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Hash should be different from original
        assert hashed != password

        # Hash should be verifiable
        assert verify_password(password, hashed) is True

    def test_password_verification_fails_with_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "SecurePassword123!"
        hashed = hash_password(password)

        # Wrong password should fail
        assert verify_password("WrongPassword!", hashed) is False

    def test_same_password_different_hashes(self):
        """Test that same password generates different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com", "user_id": "123", "role": "provider"}
        token = create_access_token(data)

        # Token should be a string
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token(self):
        """Test token verification."""
        data = {"sub": "test@example.com", "user_id": "123", "role": "provider"}
        token = create_access_token(data)

        # Verify token
        payload = verify_token(token)

        # Payload should contain original data
        assert payload["sub"] == data["sub"]
        assert payload["user_id"] == data["user_id"]
        assert payload["role"] == data["role"]

    def test_verify_invalid_token(self):
        """Test that invalid token raises exception."""
        from jose.exceptions import JWTError

        invalid_token = "invalid.token.here"

        with pytest.raises(JWTError):
            verify_token(invalid_token)


@pytest.mark.unit
@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_new_user_success(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
            "phone": "+1-555-1234",
            "role": "patient",
        }

        response = client.post("/api/auth/register", json=user_data)

        # Should return 201 Created
        assert response.status_code == status.HTTP_201_CREATED

        # Response should contain user data
        data = response.json()
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
        assert data["user"]["full_name"] == user_data["full_name"]
        assert data["user"]["role"] == user_data["role"]

        # Should contain tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Password should not be in response
        assert "password" not in data["user"]
        assert "hashed_password" not in data["user"]

        # Verify user was created in database
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.username == user_data["username"]

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username fails."""
        user_data = {
            "email": "different@example.com",
            "username": test_user.username,  # Duplicate username
            "password": "SecurePass123!",
            "full_name": "Another User",
            "role": "patient",
        }

        response = client.post("/api/auth/register", json=user_data)

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email fails."""
        user_data = {
            "email": test_user.email,  # Duplicate email
            "username": "differentuser",
            "password": "SecurePass123!",
            "full_name": "Another User",
            "role": "patient",
        }

        response = client.post("/api/auth/register", json=user_data)

        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format fails."""
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "role": "patient",
        }

        response = client.post("/api/auth/register", json=user_data)

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
@pytest.mark.auth
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success_with_username(
        self, client: TestClient, test_user: User, test_user_data: dict
    ):
        """Test successful login with username."""
        credentials = {
            "username": test_user.username,
            "password": test_user_data["password"],
        }

        response = client.post("/api/auth/login", json=credentials)

        # Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Response should contain user data and tokens
        data = response.json()
        assert data["user"]["email"] == test_user.email
        assert data["user"]["username"] == test_user.username
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_success_with_email(
        self, client: TestClient, test_user: User, test_user_data: dict
    ):
        """Test successful login with email."""
        credentials = {
            "username": test_user.email,  # Can use email as username
            "password": test_user_data["password"],
        }

        response = client.post("/api/auth/login", json=credentials)

        # Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password fails."""
        credentials = {
            "username": test_user.username,
            "password": "WrongPassword123!",
        }

        response = client.post("/api/auth/login", json=credentials)

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user fails."""
        credentials = {
            "username": "nonexistent",
            "password": "Password123!",
        }

        response = client.post("/api/auth/login", json=credentials)

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_inactive_user(
        self, client: TestClient, db_session: Session, test_user: User, test_user_data: dict
    ):
        """Test login with inactive user fails."""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()

        credentials = {
            "username": test_user.username,
            "password": test_user_data["password"],
        }

        response = client.post("/api/auth/login", json=credentials)

        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"].lower()


@pytest.mark.unit
@pytest.mark.auth
class TestGetCurrentUser:
    """Test get current user endpoint."""

    def test_get_current_user_success(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test getting current user info with valid token."""
        response = client.get("/api/auth/me", headers=auth_headers)

        # Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Should return user data
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token fails."""
        response = client.get("/api/auth/me")

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token fails."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/auth/me", headers=headers)

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
@pytest.mark.auth
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(
        self, client: TestClient, test_user: User, test_user_data: dict
    ):
        """Test successful token refresh."""
        # First login to get refresh token
        credentials = {
            "username": test_user.username,
            "password": test_user_data["password"],
        }
        login_response = client.post("/api/auth/login", json=credentials)
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/auth/refresh", json=refresh_data)

        # Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Should return new access token
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token fails."""
        refresh_data = {"refresh_token": "invalid.token.here"}
        response = client.post("/api/auth/refresh", json=refresh_data)

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
@pytest.mark.auth
class TestLogout:
    """Test logout endpoint."""

    def test_logout_success(self, client: TestClient, auth_headers: dict):
        """Test successful logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)

        # Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Should return success message
        data = response.json()
        assert "successfully logged out" in data["message"].lower()

    def test_logout_no_token(self, client: TestClient):
        """Test logout without token fails."""
        response = client.post("/api/auth/logout")

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
