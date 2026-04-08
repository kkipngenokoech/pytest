import pytest
from datetime import datetime, timedelta
from src.core.repository import InMemoryRepository


@pytest.fixture
def repository():
    return InMemoryRepository()


def test_create_and_get_user(repository):
    user = repository.create_user("testuser", "test@example.com")
    
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    retrieved_user = repository.get_user(1)
    assert retrieved_user == user


def test_get_user_by_username(repository):
    user = repository.create_user("testuser", "test@example.com")
    
    retrieved_user = repository.get_user_by_username("testuser")
    assert retrieved_user == user
    
    non_existent = repository.get_user_by_username("nonexistent")
    assert non_existent is None


def test_list_users(repository):
    user1 = repository.create_user("user1", "user1@example.com")
    user2 = repository.create_user("user2", "user2@example.com")
    
    users = repository.list_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users


def test_create_and_get_task(repository):
    user = repository.create_user("testuser", "test@example.com")
    due_date = datetime.now() + timedelta(days=1)
    
    task = repository.create_task("Test Task", "Description", user.id, due_date)
    
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "Description"
    assert task.user_id == user.id
    assert task.due_date == due_date
    assert task.completed is False
    
    retrieved_task = repository.get_task(1)
    assert retrieved_task == task


def test_list_tasks_by_user(repository):
    user1 = repository.create_user("user1", "user1@example.com")
    user2 = repository.create_user("user2", "user2@example.com")
    
    task1 = repository.create_task("Task 1", "Description 1", user1.id)
    task2 = repository.create_task("Task 2", "Description 2", user1.id)
    task3 = repository.create_task("Task 3", "Description 3", user2.id)
    
    user1_tasks = repository.list_tasks_by_user(user1.id)
    assert len(user1_tasks) == 2
    assert task1 in user1_tasks
    assert task2 in user1_tasks
    assert task3 not in user1_tasks


def test_update_task(repository):
    user = repository.create_user("testuser", "test@example.com")
    task = repository.create_task("Test Task", "Description", user.id)
    
    updated_task = repository.update_task(task.id, completed=True, title="Updated Task")
    
    assert updated_task.completed is True
    assert updated_task.title == "Updated Task"
    assert updated_task.description == "Description"  # unchanged


def test_delete_task(repository):
    user = repository.create_user("testuser", "test@example.com")
    task = repository.create_task("Test Task", "Description", user.id)
    
    assert repository.get_task(task.id) is not None
    
    result = repository.delete_task(task.id)
    assert result is True
    
    assert repository.get_task(task.id) is None
    
    # Try to delete non-existent task
    result = repository.delete_task(999)
    assert result is False


def test_create_and_get_project(repository):
    user = repository.create_user("testuser", "test@example.com")
    
    project = repository.create_project("Test Project", "Description", user.id)
    
    assert project.id == 1
    assert project.name == "Test Project"
    assert project.description == "Description"
    assert project.owner_id == user.id
    
    retrieved_project = repository.get_project(1)
    assert retrieved_project == project


def test_list_projects_by_owner(repository):
    user1 = repository.create_user("user1", "user1@example.com")
    user2 = repository.create_user("user2", "user2@example.com")
    
    project1 = repository.create_project("Project 1", "Description 1", user1.id)
    project2 = repository.create_project("Project 2", "Description 2", user1.id)
    project3 = repository.create_project("Project 3", "Description 3", user2.id)
    
    user1_projects = repository.list_projects_by_owner(user1.id)
    assert len(user1_projects) == 2
    assert project1 in user1_projects
    assert project2 in user1_projects
    assert project3 not in user1_projects
