# Import all routes
from .user_routes import router as user_router
from .task_routes import router as task_router
from .auth_routes import router as auth_router  # Added auth_routes import
from .task_status_history_routes import router as task_status_history_router