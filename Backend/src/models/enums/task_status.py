
from enum import Enum

# Define an enumeration for task statuses
class TaskStatus(str, Enum):
    # Status indicating the task is waiting to be started
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
