# Data2Paper API

This is the backend API for the Data2Paper application, built with FastAPI.

## Features

- User management (CRUD operations)
- Task management (CRUD operations)
- AI report generation (planned)

## API Endpoints

### Users

- `GET /users/` - Get all users
- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get a specific user
- `PUT /users/{user_id}` - Update a specific user
- `DELETE /users/{user_id}` - Delete a specific user

### Tasks

- `GET /tasks/` - Get all tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a specific task
- `DELETE /tasks/{task_id}` - Delete a specific task

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

3. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
src/
├── main.py              # Application entry point
├── database.py          # Database configuration
├── config.py            # Application configuration
├── models/              # Database models and CRUD operations
├── routes/              # API routes
├── schemas/             # Pydantic models for request/response validation
└── ...
```