#!/usr/bin/env python3
"""
Simple FastAPI server for manual testing
Run with: python manual_test_server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Optional
import json

app = FastAPI(
    title="Data2Paper API - Manual Test Server",
    description="A simple server for manual testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class LoginRequest(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    name: Optional[str] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str = "pending"
    user_id: int

# Mock data
users_db = [
    {"id": 1, "email": "test@example.com", "name": "Test User", "password": "password123"},
    {"id": 2, "email": "admin@example.com", "name": "Admin User", "password": "admin123"},
]

tasks_db = [
    {"id": 1, "title": "Complete project setup", "description": "Set up the development environment", "status": "completed", "user_id": 1},
    {"id": 2, "title": "Implement authentication", "description": "Add OAuth and login functionality", "status": "in_progress", "user_id": 1},
    {"id": 3, "title": "Create user dashboard", "description": "Build the main user interface", "status": "pending", "user_id": 1},
]

# Routes
@app.get("/")
async def root():
    return {"message": "Data2Paper API - Manual Test Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "manual_testing"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    # Find user by email
    user = next((u for u in users_db if u["email"] == request.email), None)
    
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Return mock token and user info
    return {
        "access_token": f"mock_token_for_{user['email']}",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }

@app.get("/users/me")
async def get_current_user():
    # Return mock current user
    return {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User"
    }

@app.get("/tasks")
async def get_tasks():
    return {"tasks": tasks_db}

@app.post("/tasks")
async def create_task(task: dict):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.get("title", "New Task"),
        "description": task.get("description", ""),
        "status": task.get("status", "pending"),
        "user_id": 1
    }
    tasks_db.append(new_task)
    return new_task

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task_update: dict):
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task fields
    for key, value in task_update.items():
        if key in task:
            task[key] = value
    
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks_db
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    tasks_db = [t for t in tasks_db if t["id"] != task_id]
    return {"message": "Task deleted successfully"}

# OAuth routes (mock)
@app.get("/oauth/providers")
async def get_oauth_providers():
    return {
        "providers": [
            {"id": "google", "name": "Google", "icon": "google", "color": "#4285f4"},
            {"id": "github", "name": "GitHub", "icon": "github", "color": "#333333"},
            {"id": "apple", "name": "Apple", "icon": "apple", "color": "#000000"}
        ],
        "enabled": True
    }

@app.post("/oauth/create-test-user/{provider}")
async def create_oauth_test_user(provider: str):
    return {
        "access_token": f"mock_oauth_token_{provider}",
        "token_type": "bearer",
        "user": {
            "id": 999,
            "email": f"oauth_user_{provider}@example.com",
            "name": f"OAuth User ({provider.title()})",
            "provider": provider
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Data2Paper Manual Test Server...")
    print("📝 Test Credentials:")
    print("   Email: test@example.com")
    print("   Password: password123")
    print("   ---")
    print("   Email: admin@example.com") 
    print("   Password: admin123")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("💡 Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
