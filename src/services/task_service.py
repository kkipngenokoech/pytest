from typing import List, Optional
from src.core.database import Database
from src.models.task import Task

class TaskService:
    def __init__(self, database: Database):
        self.db = database
    
    def create_task(self, user_id: int, title: str, description: str = "") -> Optional[Task]:
        """Create a new task"""
        query = """
            INSERT INTO tasks (user_id, title, description)
            VALUES (?, ?, ?)
        """
        
        try:
            task_id = self.db.get_last_insert_id(query, (user_id, title, description))
            return self.get_task_by_id(task_id)
        except Exception:
            return None
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        query = "SELECT * FROM tasks WHERE id = ?"
        results = self.db.execute_query(query, (task_id,))
        
        if results:
            return Task.from_dict(results[0])
        return None
    
    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """Get all tasks for a specific user"""
        query = "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC"
        results = self.db.execute_query(query, (user_id,))
        
        return [Task.from_dict(row) for row in results]
    
    def get_tasks_by_status(self, user_id: int, status: str) -> List[Task]:
        """Get tasks by status for a specific user"""
        query = "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY created_at DESC"
        results = self.db.execute_query(query, (user_id, status))
        
        return [Task.from_dict(row) for row in results]
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update task status"""
        query = "UPDATE tasks SET status = ? WHERE id = ?"
        return self.db.execute_update(query, (status, task_id)) > 0
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields"""
        if not kwargs:
            return False
        
        # Build dynamic update query
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['title', 'description', 'status']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        
        return self.db.execute_update(query, tuple(values)) > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID"""
        query = "DELETE FROM tasks WHERE id = ?"
        return self.db.execute_update(query, (task_id,)) > 0
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks across all users"""
        query = "SELECT * FROM tasks ORDER BY created_at DESC"
        results = self.db.execute_query(query)
        
        return [Task.from_dict(row) for row in results]