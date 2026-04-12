from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return self.password_hash == self.hash_password(password)
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"