import pytest
from datetime import datetime
from src.core.models import User, Task, Project


def test_user_creation():
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now()
    )
    
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)


def test_task_creation():
    due_date = datetime.now()
    task = Task(
        id=1,
        title="Test Task",
        description="A test task",
        user_id=1,
        created_at=datetime.now(),
        due_date=due_date
    )
    
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "A test task"
    assert task.user_id == 1
    assert task.completed is False
    assert task.due_date == due_date
    assert isinstance(task.created_at, datetime)


def test_project_creation():
    project = Project(
        id=1,
        name="Test Project",
        description="A test project",
        owner_id=1,
        created_at=datetime.now()
    )
    
    assert project.id == 1
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.owner_id == 1
    assert project.tasks == []
    assert isinstance(project.created_at, datetime)


def test_project_with_tasks():
    task = Task(
        id=1,
        title="Task 1",
        description="First task",
        user_id=1,
        created_at=datetime.now()
    )
    
    project = Project(
        id=1,
        name="Test Project",
        description="A test project",
        owner_id=1,
        created_at=datetime.now(),
        tasks=[task]
    )
    
    assert len(project.tasks) == 1
    assert project.tasks[0] == task
