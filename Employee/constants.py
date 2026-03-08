"""
Constants for the Employee app.
"""

from Employee.models import Designation, GovernmentIdType
from Users.models import UserRole


# Designation hierarchy: high (0) to low (5). Creator can only assign designations at or below their level.
DESIGNATION_ORDER = [
    "ORG_ADMIN",
    "OFFICE_ADMIN",
    "MANAGER",
    "SUPERVISOR",
    "EMPLOYEE",
    "SUPPORT_STAFF",
]

# User roles that can create employees, and the minimum designation index they can assign.
ROLE_MIN_DESIGNATION_INDEX = {
    UserRole.ORG_ADMIN: 0,
    UserRole.OFFICE_ADMIN: 1,
    UserRole.OFFICE_MANAGER: 2,
    UserRole.SUPERVISOR: 3,
}

# Keep same order as DESIGNATION_ORDER for indexing.
_designation_labels = dict(Designation.choices)
DESIGNATION_CHOICES_LIST = [
    {"value": v, "label": _designation_labels.get(v, v)} for v in DESIGNATION_ORDER
]

# Only these designations can be set when creating an employee (Add Employee / Import).
ALLOWED_CREATE_DESIGNATIONS = frozenset({"EMPLOYEE", "SUPPORT_STAFF"})

# Designations allowed when creating an employee with login (Manager/Supervisor).
ALLOWED_CREATE_WITH_LOGIN_DESIGNATIONS = frozenset({"MANAGER", "SUPERVISOR"})

# Government ID type allowed values (must match GovernmentIdType model choices)
GOVT_ID_VALID = {c[0] for c in GovernmentIdType.choices}

# Required columns for import
IMPORT_REQUIRED_COLUMNS = ["emp_code", "name"]
IMPORT_OPTIONAL_COLUMNS = [
    "designation",
    "gender",
    "date_of_birth",
    "email",
    "phone_number",
    "government_id_type",
    "government_id_value",
]
IMPORT_ALL_COLUMNS = IMPORT_REQUIRED_COLUMNS + IMPORT_OPTIONAL_COLUMNS

# Minimum age for DOB validation
MIN_AGE_YEARS = 18

# Chunk sizes for parallel processing and bulk create
IMPORT_VALIDATION_CHUNK_SIZE = 250
BULK_CREATE_CHUNK_SIZE = 500
IMPORT_MAX_WORKERS = 8
