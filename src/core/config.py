import os
from typing import Optional

class Config:
    """Configuration management for the application."""
    
    def __init__(self):
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
        self.port = int(os.getenv('PORT', '8000'))
        self.host = os.getenv('HOST', '0.0.0.0')
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key."""
        return getattr(self, key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        setattr(self, key, value)

config = Config()