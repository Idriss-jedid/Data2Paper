from datetime import datetime, timedelta

def example_user_crud():
    try:
        from models.model.user import user
        print("User CRUD imported successfully!")
        print(f"User CRUD instance: {user}")
        return True
    except Exception as e:
        print(f"Error importing User CRUD: {e}")
        return False

def example_task_crud():
    try:
        from models.model.task import task
        print("Task CRUD imported successfully!")
        print(f"Task CRUD instance: {task}")
        return True
    except Exception as e:
        print(f"Error importing Task CRUD: {e}")
        return False

def example_task_creation():
    """Example of how to create different types of tasks"""
    try:
        from schemas.task import TaskCreate, TaskType
        from models.enums.priority import Priority
        from models.enums.task_status import TaskStatus
        
        # Example of creating a student task
        student_task_data = {
            "title": "Complete Mathematics Assignment",
            "description": "Solve all problems in Chapter 5",
            "user_id": 1,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.STUDENT,
            "subject": "Mathematics",
            "deadline": datetime.now() + timedelta(days=7)
        }
        student_task = TaskCreate(**student_task_data)
        print(f"Student task created: {student_task}")
        
        # Example of creating a business task
        business_task_data = {
            "title": "Prepare Quarterly Report",
            "description": "Compile sales data and create presentation",
            "user_id": 1,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.BUSINESS,
            "project_name": "Q3 Sales Report",
            "priority": Priority.HIGH,
            "due_date": datetime.now() + timedelta(days=14)
        }
        business_task = TaskCreate(**business_task_data)
        print(f"Business task created: {business_task}")
        
        # Example of creating an employment task
        employment_task_data = {
            "title": "Prepare for Interview",
            "description": "Research company and prepare answers",
            "user_id": 1,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.EMPLOYMENT,
            "company": "Tech Corp",
            "position": "Software Engineer",
            "deadline": datetime.now() + timedelta(days=3)
        }
        employment_task = TaskCreate(**employment_task_data)
        print(f"Employment task created: {employment_task}")
        
        # Example of creating a certification task
        certification_task_data = {
            "title": "Renew AWS Certification",
            "description": "Complete required courses and pass exam",
            "user_id": 1,
            "status": TaskStatus.PENDING,
            "task_type": TaskType.CERTIFICATION,
            "certification_name": "AWS Certified Solutions Architect",
            "issuer": "Amazon Web Services",
            "expiry_date": datetime.now() + timedelta(days=365)
        }
        certification_task = TaskCreate(**certification_task_data)
        print(f"Certification task created: {certification_task}")
        
        return True
    except Exception as e:
        print(f"Error creating example tasks: {e}")
        return False

def main():
    print("Testing CRUD imports without database connection...")
    
    # Test imports
    user_success = example_user_crud()
    task_success = example_task_crud()
    example_tasks_success = example_task_creation()
    
    if user_success and task_success and example_tasks_success:
        print("\nAll CRUD imports and examples successful!")
        print("\nTo use these CRUD operations with a database:")
        print("1. Make sure you have the correct database configuration in your .env file")
        print("2. Install all required dependencies:")
        print("   pip install -r requirements.txt")
        print("3. Ensure your database is running and accessible")
        print("4. Run the full example with database connection")
    else:
        print("\nSome imports or examples failed. Please check the errors above.")

if __name__ == "__main__":
    main()