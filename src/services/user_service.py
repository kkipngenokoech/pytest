from typing import List, Optional
from src.core.database import Database
from src.models.user import User

class UserService:
    def __init__(self, database: Database):
        self.db = database
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user"""
        password_hash = User.hash_password(password)
        
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """
        
        try:
            user_id = self.db.get_last_insert_id(query, (username, email, password_hash))
            return self.get_user_by_id(user_id)
        except Exception:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.db.execute_query(query, (user_id,))
        
        if results:
            return User.from_dict(results[0])
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        results = self.db.execute_query(query, (username,))
        
        if results:
            return User.from_dict(results[0])
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.db.execute_query(query, (email,))
        
        if results:
            return User.from_dict(results[0])
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        
        if user and user.verify_password(password):
            return user
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        results = self.db.execute_query(query)
        
        return [User.from_dict(row) for row in results]
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        if not kwargs:
            return False
        
        # Build dynamic update query
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['username', 'email', 'password_hash']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        
        return self.db.execute_update(query, tuple(values)) > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        query = "DELETE FROM users WHERE id = ?"
        return self.db.execute_update(query, (user_id,)) > 0