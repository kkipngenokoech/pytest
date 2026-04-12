from sqlalchemy.orm import Session
from ..models.user import User
from ..core.database import get_db
from typing import Optional, List
import hashlib

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, password: str) -> User:
        hashed_password = self._hash_password(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()