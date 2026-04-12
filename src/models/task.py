from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: Optional[int] = None
    user_id: int = 0
    title: str = ""
    description: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', 0),
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task instance to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at
        }
    
    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', status='{self.status}')"