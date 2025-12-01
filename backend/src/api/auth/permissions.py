from enum import Enum
from typing import Set, Dict
from src.api.models.user import UserRole

class Permission(str, Enum):
    """Granular permissions for the application."""
    
    # Patient Permissions
    VIEW_PATIENT = "view_patient"
    EDIT_PATIENT = "edit_patient"
    CREATE_PATIENT = "create_patient"
    DELETE_PATIENT = "delete_patient"
    
    # Clinical Permissions
    VIEW_CLINICAL_DATA = "view_clinical_data"
    EDIT_CLINICAL_DATA = "edit_clinical_data"
    PRESCRIBE_MEDICATION = "prescribe_medication"
    
    # Appointment Permissions
    VIEW_APPOINTMENT = "view_appointment"
    MANAGE_APPOINTMENT = "manage_appointment"
    
    # User Management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # System
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_TENANT = "manage_tenant"

    # CarePrep
    SUBMIT_PREVISIT_DATA = "submit_previsit_data"
    VIEW_OWN_DATA = "view_own_data"

# Role to Permissions Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.PATIENT: {
        Permission.VIEW_APPOINTMENT,
        Permission.SUBMIT_PREVISIT_DATA,
        Permission.VIEW_OWN_DATA,
    },
    UserRole.DOCTOR: {
        Permission.VIEW_PATIENT,
        Permission.EDIT_PATIENT,
        Permission.CREATE_PATIENT,
        Permission.VIEW_CLINICAL_DATA,
        Permission.EDIT_CLINICAL_DATA,
        Permission.PRESCRIBE_MEDICATION,
        Permission.VIEW_APPOINTMENT,
        Permission.MANAGE_APPOINTMENT,
    },
    UserRole.NURSE: {
        Permission.VIEW_PATIENT,
        Permission.EDIT_PATIENT,
        Permission.VIEW_CLINICAL_DATA,
        Permission.EDIT_CLINICAL_DATA,
        Permission.VIEW_APPOINTMENT,
        Permission.MANAGE_APPOINTMENT,
    },
    UserRole.STAFF: {
        Permission.VIEW_PATIENT,
        Permission.VIEW_APPOINTMENT,
        Permission.MANAGE_APPOINTMENT,
    },
    UserRole.ADMIN: {
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_TENANT,
        Permission.VIEW_PATIENT, # Admin might need to view patient list for admin purposes
    },
    UserRole.SUPER_ADMIN: set(Permission), # All permissions
}

def get_role_permissions(role: UserRole) -> Set[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())
