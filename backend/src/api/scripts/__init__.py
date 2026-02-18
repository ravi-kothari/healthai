"""
Scripts package for database seeding and maintenance.

Available scripts:
- seed_roles: Seed default roles and permissions
- migrate_user_roles: Migrate users from legacy role enum to new scoped system
"""

from src.api.scripts.seed_roles import seed_default_roles, verify_roles_seeded
from src.api.scripts.migrate_user_roles import migrate_user_roles, verify_migration

__all__ = [
    "seed_default_roles",
    "verify_roles_seeded",
    "migrate_user_roles",
    "verify_migration",
]
