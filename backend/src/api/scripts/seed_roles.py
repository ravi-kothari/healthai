"""
Seed default roles and permissions.

This script ensures all default roles exist in the database.
It can be run multiple times safely (idempotent).

Usage:
    python -m src.api.scripts.seed_roles

Or from within the application:
    from src.api.scripts.seed_roles import seed_default_roles
    seed_default_roles(db_session)
"""

import logging
from sqlalchemy.orm import Session
from typing import Optional

from src.api.database import SessionLocal
from src.api.models.role import Role, DEFAULT_ROLES, RoleScope

logger = logging.getLogger(__name__)


def seed_default_roles(db: Session) -> dict:
    """
    Seed all default roles into the database.

    This function is idempotent - it will:
    - Create roles that don't exist
    - Update permissions for existing roles if they've changed
    - Never delete roles

    Args:
        db: Database session

    Returns:
        dict with counts of created and updated roles
    """
    created = 0
    updated = 0
    unchanged = 0

    for role_config in DEFAULT_ROLES:
        existing_role = db.query(Role).filter(Role.name == role_config["name"]).first()

        if existing_role:
            # Check if permissions need updating
            if set(existing_role.permissions) != set(role_config["permissions"]):
                logger.info(f"Updating permissions for role: {role_config['name']}")
                existing_role.permissions = role_config["permissions"]
                existing_role.display_name = role_config["display_name"]
                existing_role.description = role_config["description"]
                updated += 1
            else:
                unchanged += 1
        else:
            # Create new role
            logger.info(f"Creating role: {role_config['name']}")
            role = Role(
                name=role_config["name"],
                display_name=role_config["display_name"],
                description=role_config["description"],
                scope=role_config["scope"],
                permissions=role_config["permissions"],
                is_system=role_config["is_system"],
            )
            db.add(role)
            created += 1

    db.commit()

    result = {
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "total": len(DEFAULT_ROLES),
    }

    logger.info(f"Seed roles complete: {result}")
    return result


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """
    Get a role by its name.

    Args:
        db: Database session
        name: Role name

    Returns:
        Role or None
    """
    return db.query(Role).filter(Role.name == name).first()


def list_all_roles(db: Session) -> list:
    """
    List all roles in the database.

    Args:
        db: Database session

    Returns:
        List of role dictionaries
    """
    roles = db.query(Role).order_by(Role.scope, Role.name).all()
    return [role.to_dict() for role in roles]


def verify_roles_seeded(db: Session) -> bool:
    """
    Verify that all default roles are seeded.

    Args:
        db: Database session

    Returns:
        True if all roles exist
    """
    for role_config in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.name == role_config["name"]).first()
        if not role:
            logger.warning(f"Missing role: {role_config['name']}")
            return False
    return True


def main():
    """Main entry point for the seed script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Starting role seeding...")

    db = SessionLocal()
    try:
        result = seed_default_roles(db)
        print(f"\nRole seeding complete:")
        print(f"  Created: {result['created']}")
        print(f"  Updated: {result['updated']}")
        print(f"  Unchanged: {result['unchanged']}")
        print(f"  Total: {result['total']}")

        # Verify
        if verify_roles_seeded(db):
            print("\nAll default roles verified.")
        else:
            print("\nWARNING: Some roles may be missing!")

        # List all roles
        print("\nCurrent roles:")
        for role in list_all_roles(db):
            print(f"  - {role['name']} ({role['scope']}): {len(role['permissions'])} permissions")

    except Exception as e:
        logger.error(f"Error seeding roles: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
