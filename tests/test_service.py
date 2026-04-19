import pytest
from datetime import datetime, timedelta
from src.core.service import TaskManagementService
from src.core.repository import InMemoryRepository


@pytest.fixture
def service():
    repository = InMemoryRepository()
    return TaskManagementService(repository)


def test_register_user(service):
    user = service.register_user("testuser", "test@example.com")
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_register_duplicate_user(service):
    service.register_user("testuser", "test@example.com")
    
    with pytest.raises(ValueError, match="User with username 'testuser' already exists"):
        service.register_user("testuser", "another@example.com")


def test_get_user(service):
    user = service.register_user("testuser", "test@example.com")
    
    retrieved_user = service.get_user(user.id)
    assert retrieved_user == user
    
    non_existent = service.get_user(999)
    assert non_existent is None


def test_create_task(service):
    user = service.register_user("testuser", "test@example.com")
    due_date = datetime.now() + timedelta(days=1)
    
    task = service.create_task("Test Task", "Description", user.id, due_date)
    
    assert task.title == "Test Task"
    assert task.description == "Description"
    assert task.user_id == user.id
    assert task.due_date == due_date
    assert task.completed is False


def test_create_task_invalid_user(service):
    with pytest.raises(ValueError, match="User with id 999 does not exist"):
        service.create_task("Test Task", "Description", 999)


def test_get_user_tasks(service):
    user = service.register_user("testuser", "test@example.com")
    
    task1 = service.create_task("Task 1", "Description 1", user.id)
    task2 = service.create_task("Task 2", "Description 2", user.id)
    
    tasks = service.get_user_tasks(user.id)
    assert len(tasks) == 2
    assert task1 in tasks
    assert task2 in tasks


def test_get_user_tasks_invalid_user(service):
    with pytest.raises(ValueError, match="User with id 999 does not exist"):
        service.get_user_tasks(999)


def test_complete_task(service):
    user = service.register_user("testuser", "test@example.com")
    task = service.create_task("Test Task", "Description", user.id)
    
    completed_task = service.complete_task(task.id, user.id)
    
    assert completed_task.completed is True
    assert completed_task.id == task.id


def test_complete_task_invalid_task(service):
    user = service.register_user("testuser", "test@example.com")
    
    with pytest.raises(ValueError, match="Task with id 999 does not exist"):
        service.complete_task(999, user.id)


def test_complete_task_wrong_user(service):
    user1 = service.register_user("user1", "user1@example.com")
    user2 = service.register_user("user2", "user2@example.com")
    
    task = service.create_task("Test Task", "Description", user1.id)
    
    with pytest.raises(ValueError, match="User can only complete their own tasks"):
        service.complete_task(task.id, user2.id)


def test_delete_task(service):
    user = service.register_user("testuser", "test@example.com")
    task = service.create_task("Test Task", "Description", user.id)
    
    result = service.delete_task(task.id, user.id)
    assert result is True
    
    # Verify task is deleted
    tasks = service.get_user_tasks(user.id)
    assert len(tasks) == 0


def test_delete_task_invalid_task(service):
    user = service.register_user("testuser", "test@example.com")
    
    with pytest.raises(ValueError, match="Task with id 999 does not exist"):
        service.delete_task(999, user.id)


def test_delete_task_wrong_user(service):
    user1 = service.register_user("user1", "user1@example.com")
    user2 = service.register_user("user2", "user2@example.com")
    
    task = service.create_task("Test Task", "Description", user1.id)
    
    with pytest.raises(ValueError, match="User can only delete their own tasks"):
        service.delete_task(task.id, user2.id)


def test_create_project(service):
    user = service.register_user("testuser", "test@example.com")
    
    project = service.create_project("Test Project", "Description", user.id)
    
    assert project.name == "Test Project"
    assert project.description == "Description"
    assert project.owner_id == user.id


def test_create_project_invalid_user(service):
    with pytest.raises(ValueError, match="User with id 999 does not exist"):
        service.create_project("Test Project", "Description", 999)


def test_get_user_projects(service):
    user = service.register_user("testuser", "test@example.com")
    
    project1 = service.create_project("Project 1", "Description 1", user.id)
    project2 = service.create_project("Project 2", "Description 2", user.id)
    
    projects = service.get_user_projects(user.id)
    assert len(projects) == 2
    assert project1 in projects
    assert project2 in projects


def test_get_user_projects_invalid_user(service):
    with pytest.raises(ValueError, match="User with id 999 does not exist"):
        service.get_user_projects(999)


def test_get_overdue_tasks(service):
    user = service.register_user("testuser", "test@example.com")
    
    # Create tasks with different due dates
    past_date = datetime.now() - timedelta(days=1)
    future_date = datetime.now() + timedelta(days=1)
    
    overdue_task = service.create_task("Overdue Task", "Description", user.id, past_date)
    future_task = service.create_task("Future Task", "Description", user.id, future_date)
    no_due_date_task = service.create_task("No Due Date", "Description", user.id)
    
    # Complete the overdue task to test it's not included
    completed_overdue = service.create_task("Completed Overdue", "Description", user.id, past_date)
    service.complete_task(completed_overdue.id, user.id)
    
    overdue_tasks = service.get_overdue_tasks(user.id)
    
    assert len(overdue_tasks) == 1
    assert overdue_task in overdue_tasks
    assert future_task not in overdue_tasks
    assert no_due_date_task not in overdue_tasks
    assert completed_overdue not in overdue_tasks
