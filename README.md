# Data2Paper

A backend application for managing tasks and generating reports based on data input.

## Project Overview

Data2Paper is a backend-heavy application focused on managing different types of tasks and generating AI-powered reports based on data input. The project targets users who need to convert structured data into formal reports or documents.

## Features

- Task Management: Create, track, and update various types of tasks
- Report Generation: Generate AI-based reports using processed data
- User Management: Role-based access control and status tracking
- Status History Tracking: Maintain history of task state changes

## Technology Stack

- Backend: Python
- ORM: SQLAlchemy with Alembic for migrations
- Database: (To be configured)

## Project Structure

```
Backend/
└── src/
    └── models/
        ├── db_schemes/
        │   ├── alembic/
        │   ├── schemes/
        │   └── alembic.ini
        ├── enums/
        ├── model/
        └── __init__.py
```

## Setup Instructions

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure database and Alembic settings

3. Run migrations:
   ```
   alembic upgrade head
   ```

## Development

This project follows a layered architecture pattern with clear separation of concerns:
- API layer
- Business logic layer
- Data access layer

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.