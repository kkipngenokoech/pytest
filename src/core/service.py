from typing import List, Optional
from datetime import datetime
from .models import User, Task, Project
from .repository import InMemoryRepository


class TaskManagementService:
    def __init__(self, repository: InMemoryRepository):
        self.repository = repository
    
    def register_user(self, username: str, email: str) -> User:
        existing_user = self.repository.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"User with username '{username}' already exists")
        
        return self.repository.create_user(username, email)
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.get_user(user_id)
    
    def create_task(self, title: str, description: str, user_id: int, due_date: Optional[datetime] = None) -> Task:
        user = self.repository.get_user(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")
        
        return self.repository.create_task(title, description, user_id, due_date)
    
    def get_user_tasks(self, user_id: int) -> List[Task]:
        user = self.repository.get_user(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")
        
        return self.repository.list_tasks_by_user(user_id)
    
    def complete_task(self, task_id: int, user_id: int) -> Task:
        task = self.repository.get_task(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} does not exist")
        
        if task.user_id != user_id:
            raise ValueError("User can only complete their own tasks")
        
        updated_task = self.repository.update_task(task_id, completed=True)
        return updated_task
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        task = self.repository.get_task(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} does not exist")
        
        if task.user_id != user_id:
            raise ValueError("User can only delete their own tasks")
        
        return self.repository.delete_task(task_id)
    
    def create_project(self, name: str, description: str, owner_id: int) -> Project:
        user = self.repository.get_user(owner_id)
        if not user:
            raise ValueError(f"User with id {owner_id} does not exist")
        
        return self.repository.create_project(name, description, owner_id)
    
    def get_user_projects(self, user_id: int) -> List[Project]:
        user = self.repository.get_user(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")
        
        return self.repository.list_projects_by_owner(user_id)
    
    def get_overdue_tasks(self, user_id: int) -> List[Task]:
        tasks = self.get_user_tasks(user_id)
        now = datetime.now()
        
        overdue_tasks = []
        for task in tasks:
            if task.due_date and task.due_date < now and not task.completed:
                overdue_tasks.append(task)
        
        return overdue_tasks
