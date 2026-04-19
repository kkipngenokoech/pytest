from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    user: str = "postgres"
    password: str = ""
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            name=os.getenv('DB_NAME', 'myapp'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )


@dataclass
class AppConfig:
    debug: bool = False
    secret_key: str = "dev-secret-key"
    database: DatabaseConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key'),
            database=DatabaseConfig.from_env()
        )


config = AppConfig.from_env()
