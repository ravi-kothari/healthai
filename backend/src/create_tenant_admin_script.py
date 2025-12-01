import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

# Assuming running from /app, so src is in path
from src.api.database import Base, get_db
from src.api.models.user import User, UserRole
from src.api.models.tenant import Tenant, TenantStatus
from src.api.auth.password import hash_password
from src.api.config import settings
from src.api.models.appointment import Appointment
from src.api.models.careprep import CarePrepResponse
from src.api.models.patient import Patient

def create_tenant_admin():
    # Database connection
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Tenant
        tenant_name = "Verification Clinic"
        tenant_slug = "verification-clinic"
        
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not tenant:
            print(f"Creating tenant: {tenant_name}")
            tenant = Tenant(
                name=tenant_name,
                slug=tenant_slug,
                email="admin@verification.com",
                subscription_plan="professional",
                status=TenantStatus.ACTIVE,
                is_active=True
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        else:
            print(f"Tenant already exists: {tenant.id}")

        # 2. Create Tenant Admin User
        admin_email = "admin@verification.com"
        admin_username = "verify_admin"
        admin_password = "VerifyPass123!"
        
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"Creating admin user: {admin_email}")
            admin = User(
                email=admin_email,
                username=admin_username,
                hashed_password=hash_password(admin_password),
                full_name="Verification Admin",
                role=UserRole.ADMIN,
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin user created successfully.")
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
        else:
            print(f"Admin user already exists: {admin.id}")
            # Ensure password is correct (resetting it)
            admin.hashed_password = hash_password(admin_password)
            admin.tenant_id = tenant.id # Ensure linked to correct tenant
            admin.role = UserRole.ADMIN
            db.commit()
            print(f"Admin user updated with known password.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tenant_admin()
