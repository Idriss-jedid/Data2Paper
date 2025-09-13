from fastapi import FastAPI
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import user_routes, task_routes

app = FastAPI(title="Data2Paper API",description="API for managing tasks and generating reports",version="0.1.0")

# Include routers
app.include_router(user_routes.router)
app.include_router(task_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Data2Paper API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

