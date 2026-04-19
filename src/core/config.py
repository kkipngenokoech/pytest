import os
from pathlib import Path

class Config:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.output_dir = self.base_dir / "output"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    @property
    def database_url(self):
        return os.getenv("DATABASE_URL", "sqlite:///app.db")
    
    @property
    def debug(self):
        return os.getenv("DEBUG", "False").lower() == "true"

config = Config()