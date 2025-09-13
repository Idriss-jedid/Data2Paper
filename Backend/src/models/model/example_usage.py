
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

def main():
    print("Testing CRUD imports without database connection...")
    
    # Test imports
    user_success = example_user_crud()
    task_success = example_task_crud()
    
    if user_success and task_success:
        print("\nAll CRUD imports successful!")
        print("\nTo use these CRUD operations with a database:")
        print("1. Make sure you have the correct database configuration in your .env file")
        print("2. Install all required dependencies:")
        print("   pip install -r requirements.txt")
        print("3. Ensure your database is running and accessible")
        print("4. Run the full example with database connection")
    else:
        print("\nSome imports failed. Please check the errors above.")

if __name__ == "__main__":
    main()