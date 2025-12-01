
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.api.models.user import User, UserRole
from src.api.models.tenant import Tenant
from src.api.auth.password import hash_password

@pytest.mark.integration
class TestProviderSettingsAPI:
    """Integration tests for provider settings endpoints."""

    @pytest.fixture
    def tenant_admin(self, db_session: Session, test_tenant: Tenant):
        """Create a tenant admin user."""
        user = User(
            email="admin@example.com",
            username="tenant_admin",
            hashed_password=hash_password("SecurePass123!"),
            full_name="Tenant Admin",
            role=UserRole.ADMIN,
            tenant_id=test_tenant.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.fixture
    def tenant_member(self, db_session: Session, test_tenant: Tenant):
        """Create a regular member user."""
        user = User(
            email="member@example.com",
            username="tenant_member",
            hashed_password=hash_password("SecurePass123!"),
            full_name="Tenant Member",
            role=UserRole.PATIENT, # Using PATIENT as a generic non-admin role for now
            tenant_id=test_tenant.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.fixture
    def admin_token(self, client: TestClient, tenant_admin: User):
        """Get access token for tenant admin."""
        response = client.post("/api/auth/login", json={
            "username": tenant_admin.username,
            "password": "SecurePass123!"
        })
        return response.json()["access_token"]

    def test_list_users(self, client: TestClient, admin_token: str, tenant_admin: User, tenant_member: User):
        """Test listing users in the tenant."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/auth/users", headers=headers)
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2
        user_ids = [u["id"] for u in users]
        assert str(tenant_admin.id) in user_ids
        assert str(tenant_member.id) in user_ids

    def test_update_user_role(self, client: TestClient, admin_token: str, tenant_member: User):
        """Test updating a user's role."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_role = "doctor"
        
        response = client.put(
            f"/api/auth/users/{tenant_member.id}/role",
            headers=headers,
            json={"role": new_role}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == new_role
        assert data["id"] == str(tenant_member.id)

    def test_list_users_unauthorized(self, client: TestClient, tenant_member: User):
        """Test that non-admins cannot list users."""
        # Login as member
        response = client.post("/api/auth/login", json={
            "username": tenant_member.username,
            "password": "SecurePass123!"
        })
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/auth/users", headers=headers)
        assert response.status_code == 403
