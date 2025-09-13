from enum import Enum

class UserRole(str, Enum):
    STUDENT = "Student"
    EMPLOYEE = "Employee"
    ADMIN = "Admin"
    USER = "User"  # Default user role
