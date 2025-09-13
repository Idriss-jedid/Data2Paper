
from enum import Enum

class ReportType(str, Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"
