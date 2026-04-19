from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import User, Task, Project


class InMemoryRepository:
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._tasks: Dict[int, Task] = {}
        self._projects: Dict[int, Project] = {}
        self._next_user_id = 1
        self._next_task_id = 1
        self._next_project_id = 1
    
    def create_user(self, username: str, email: str) -> User:
        user = User(
            id=self._next_user_id,
            username=username,
            email=email,
            created_at=datetime.now()
        )
        self._users[user.id] = user
        self._next_user_id += 1
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    def list_users(self) -> List[User]:
        return list(self._users.values())
    
    def create_task(self, title: str, description: str, user_id: int, due_date: Optional[datetime] = None) -> Task:
        task = Task(
            id=self._next_task_id,
            title=title,
            description=description,
            user_id=user_id,
            created_at=datetime.now(),
            due_date=due_date
        )
        self._tasks[task.id] = task
        self._next_task_id += 1
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def list_tasks_by_user(self, user_id: int) -> List[Task]:
        return [task for task in self._tasks.values() if task.user_id == user_id]
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        return task
    
    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def create_project(self, name: str, description: str, owner_id: int) -> Project:
        project = Project(
            id=self._next_project_id,
            name=name,
            description=description,
            owner_id=owner_id,
            created_at=datetime.now()
        )
        self._projects[project.id] = project
        self._next_project_id += 1
        return project
    
    def get_project(self, project_id: int) -> Optional[Project]:
        return self._projects.get(project_id)
    
    def list_projects_by_owner(self, owner_id: int) -> List[Project]:
        return [project for project in self._projects.values() if project.owner_id == owner_id]
