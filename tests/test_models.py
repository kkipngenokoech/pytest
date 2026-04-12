import pytest
from datetime import datetime
from src.core.models import User, Post, Comment


def test_user_creation():
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now()
    )
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_post_creation():
    post = Post(
        id=1,
        title="Test Post",
        content="This is a test post",
        author_id=1,
        created_at=datetime.now()
    )
    assert post.id == 1
    assert post.title == "Test Post"
    assert post.content == "This is a test post"
    assert post.author_id == 1
    assert post.is_published is False
    assert post.updated_at is None


def test_comment_creation():
    comment = Comment(
        id=1,
        content="Test comment",
        post_id=1,
        author_id=1,
        created_at=datetime.now()
    )
    assert comment.id == 1
    assert comment.content == "Test comment"
    assert comment.post_id == 1
    assert comment.author_id == 1
    assert comment.parent_id is None


def test_comment_with_parent():
    comment = Comment(
        id=2,
        content="Reply comment",
        post_id=1,
        author_id=1,
        created_at=datetime.now(),
        parent_id=1
    )
    assert comment.parent_id == 1
