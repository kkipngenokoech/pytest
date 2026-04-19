from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True


@dataclass
class Post:
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_published: bool = False


@dataclass
class Comment:
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime
    parent_id: Optional[int] = None
