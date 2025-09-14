
from enum import Enum

class ReportType(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"
