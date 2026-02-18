"""
Migrate existing users from legacy role enum to new scoped role system.

This script:
1. Checks if roles are seeded
2. For each user with a legacy_role:
   - Creates appropriate UserRole assignment
   - Maps old roles to new roles

Role Mapping:
- super_admin -> super_admin (platform scope)
- admin -> tenant_admin (tenant scope)
- doctor -> provider (tenant scope)
- nurse -> provider (tenant scope)
- staff -> staff (tenant scope)
- patient -> patient (tenant scope)

Usage:
    python -m src.api.scripts.migrate_user_roles

Or from within the application:
    from src.api.scripts.migrate_user_roles import migrate_user_roles
    migrate_user_roles(db_session)
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from typing import Optional

from src.api.database import SessionLocal
from src.api.models.user import User
from src.api.models.role import Role, UserRole as UserRoleModel, RoleScope
from src.api.scripts.seed_roles import seed_default_roles, verify_roles_seeded

logger = logging.getLogger(__name__)

# Mapping from old role enum values to new role names
ROLE_MAPPING = {
    "super_admin": ("super_admin", RoleScope.PLATFORM),
    "admin": ("tenant_admin", RoleScope.TENANT),
    "doctor": ("provider", RoleScope.TENANT),
    "nurse": ("provider", RoleScope.TENANT),
    "staff": ("staff", RoleScope.TENANT),
    "patient": ("patient", RoleScope.TENANT),
}


def get_legacy_role(db: Session, user: User) -> Optional[str]:
    """
    Get the legacy role value for a user.

    This queries the legacy_role column directly since it may have been
    renamed from 'role' by the migration.

    Args:
        db: Database session
        user: User object

    Returns:
        Legacy role string or None
    """
    # Try to get legacy_role directly from the model if it exists
    if hasattr(user, 'legacy_role'):
        return user.legacy_role

    # Otherwise, query the database directly
    try:
        result = db.execute(
            text("SELECT legacy_role FROM users WHERE id = :user_id"),
            {"user_id": user.id}
        )
        row = result.fetchone()
        if row:
            return row[0]
    except Exception as e:
        # Column might not exist yet (pre-migration)
        logger.debug(f"Could not get legacy_role: {e}")

    # Fall back to role attribute if it exists
    if hasattr(user, 'role') and user.role:
        return user.role.value if hasattr(user.role, 'value') else str(user.role)

    return None


def migrate_user_roles(db: Session, dry_run: bool = False) -> dict:
    """
    Migrate all users from legacy role to new role system.

    Args:
        db: Database session
        dry_run: If True, don't commit changes, just report what would happen

    Returns:
        dict with migration statistics
    """
    # Ensure roles are seeded first
    if not verify_roles_seeded(db):
        logger.info("Seeding default roles first...")
        seed_default_roles(db)

    stats = {
        "migrated": 0,
        "skipped_already_migrated": 0,
        "skipped_no_legacy_role": 0,
        "skipped_no_mapping": 0,
        "errors": 0,
        "total_users": 0,
    }

    # Get all users
    users = db.query(User).all()
    stats["total_users"] = len(users)

    # Pre-load roles for efficiency
    roles_by_name = {role.name: role for role in db.query(Role).all()}

    for user in users:
        try:
            # Check if user already has roles assigned
            existing_roles = db.query(UserRoleModel).filter(
                UserRoleModel.user_id == user.id
            ).count()

            if existing_roles > 0:
                stats["skipped_already_migrated"] += 1
                continue

            # Get legacy role
            legacy_role = get_legacy_role(db, user)

            if not legacy_role:
                stats["skipped_no_legacy_role"] += 1
                continue

            # Get mapping
            mapping = ROLE_MAPPING.get(legacy_role)
            if not mapping:
                logger.warning(f"No mapping for role: {legacy_role} (user: {user.id})")
                stats["skipped_no_mapping"] += 1
                continue

            new_role_name, scope_type = mapping

            # Get the role
            role = roles_by_name.get(new_role_name)
            if not role:
                logger.error(f"Role not found: {new_role_name}")
                stats["errors"] += 1
                continue

            # Determine scope_id
            scope_id = None
            if scope_type == RoleScope.TENANT:
                if not user.tenant_id:
                    logger.warning(f"User {user.id} has tenant role but no tenant_id")
                    stats["errors"] += 1
                    continue
                scope_id = user.tenant_id

            # Create user role assignment
            if not dry_run:
                user_role = UserRoleModel(
                    user_id=user.id,
                    role_id=role.id,
                    scope_type=scope_type,
                    scope_id=scope_id,
                    is_primary=True,
                    granted_at=datetime.now(timezone.utc)
                )
                db.add(user_role)

            stats["migrated"] += 1
            logger.info(f"{'Would migrate' if dry_run else 'Migrated'} user {user.id}: {legacy_role} -> {new_role_name} ({scope_type})")

        except Exception as e:
            logger.error(f"Error migrating user {user.id}: {e}")
            stats["errors"] += 1

    if not dry_run:
        db.commit()

    return stats


def verify_migration(db: Session) -> dict:
    """
    Verify that all users have been migrated to the new role system.

    Args:
        db: Database session

    Returns:
        dict with verification results
    """
    total_users = db.query(User).count()
    users_with_roles = db.query(User).join(
        UserRoleModel, User.id == UserRoleModel.user_id
    ).distinct().count()

    # Get role distribution
    role_counts = db.query(
        Role.name,
        db.query(UserRoleModel).filter(UserRoleModel.role_id == Role.id).count()
    ).all()

    return {
        "total_users": total_users,
        "users_with_roles": users_with_roles,
        "users_without_roles": total_users - users_with_roles,
        "migration_complete": total_users == users_with_roles,
        "role_distribution": {name: count for name, count in role_counts if count > 0}
    }


def main():
    """Main entry point for the migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate users to new role system")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't commit changes, just report what would happen"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify migration status, don't migrate"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    db = SessionLocal()
    try:
        if args.verify_only:
            print("\nVerifying migration status...")
            result = verify_migration(db)
            print(f"  Total users: {result['total_users']}")
            print(f"  Users with roles: {result['users_with_roles']}")
            print(f"  Users without roles: {result['users_without_roles']}")
            print(f"  Migration complete: {result['migration_complete']}")
            if result.get('role_distribution'):
                print("  Role distribution:")
                for role, count in result['role_distribution'].items():
                    print(f"    - {role}: {count}")
        else:
            mode = "DRY RUN" if args.dry_run else "LIVE"
            print(f"\nStarting user role migration ({mode})...")

            result = migrate_user_roles(db, dry_run=args.dry_run)

            print(f"\nMigration complete ({mode}):")
            print(f"  Migrated: {result['migrated']}")
            print(f"  Skipped (already migrated): {result['skipped_already_migrated']}")
            print(f"  Skipped (no legacy role): {result['skipped_no_legacy_role']}")
            print(f"  Skipped (no mapping): {result['skipped_no_mapping']}")
            print(f"  Errors: {result['errors']}")
            print(f"  Total users: {result['total_users']}")

            if args.dry_run:
                print("\nThis was a dry run. Run without --dry-run to apply changes.")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
