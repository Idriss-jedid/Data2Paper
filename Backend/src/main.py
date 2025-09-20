from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import user_router, task_router, auth_router, task_status_history_router
from routes.ai_report_routes import router as ai_report_router
from routes.oauth_routes import router as oauth_router

app = FastAPI(title="Data2Paper API",description="API for managing tasks and generating reports",version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(task_status_history_router)
app.include_router(ai_report_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Data2Paper API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}