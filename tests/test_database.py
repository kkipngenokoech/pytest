import pytest
from src.core.database import Database
from src.core.models import User, Post, Comment


@pytest.fixture
def db():
    return Database()


def test_create_user(db):
    user = db.create_user("testuser", "test@example.com")
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_get_user(db):
    user = db.create_user("testuser", "test@example.com")
    retrieved_user = db.get_user(user.id)
    assert retrieved_user == user


def test_get_nonexistent_user(db):
    user = db.get_user(999)
    assert user is None


def test_get_user_by_username(db):
    user = db.create_user("testuser", "test@example.com")
    retrieved_user = db.get_user_by_username("testuser")
    assert retrieved_user == user


def test_get_user_by_nonexistent_username(db):
    user = db.get_user_by_username("nonexistent")
    assert user is None


def test_create_post(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    assert post.id == 1
    assert post.title == "Test Post"
    assert post.content == "Content"
    assert post.author_id == user.id


def test_create_post_invalid_author(db):
    post = db.create_post("Test Post", "Content", 999)
    assert post is None


def test_get_post(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    retrieved_post = db.get_post(post.id)
    assert retrieved_post == post


def test_get_posts_by_author(db):
    user = db.create_user("testuser", "test@example.com")
    post1 = db.create_post("Post 1", "Content 1", user.id)
    post2 = db.create_post("Post 2", "Content 2", user.id)
    
    posts = db.get_posts_by_author(user.id)
    assert len(posts) == 2
    assert post1 in posts
    assert post2 in posts


def test_create_comment(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    comment = db.create_comment("Test comment", post.id, user.id)
    
    assert comment.id == 1
    assert comment.content == "Test comment"
    assert comment.post_id == post.id
    assert comment.author_id == user.id
    assert comment.parent_id is None


def test_create_comment_invalid_post(db):
    user = db.create_user("testuser", "test@example.com")
    comment = db.create_comment("Test comment", 999, user.id)
    assert comment is None


def test_create_comment_invalid_author(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    comment = db.create_comment("Test comment", post.id, 999)
    assert comment is None


def test_create_reply_comment(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    parent_comment = db.create_comment("Parent comment", post.id, user.id)
    reply_comment = db.create_comment("Reply comment", post.id, user.id, parent_comment.id)
    
    assert reply_comment.parent_id == parent_comment.id


def test_create_reply_comment_invalid_parent(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    comment = db.create_comment("Test comment", post.id, user.id, 999)
    assert comment is None


def test_get_comments_by_post(db):
    user = db.create_user("testuser", "test@example.com")
    post = db.create_post("Test Post", "Content", user.id)
    comment1 = db.create_comment("Comment 1", post.id, user.id)
    comment2 = db.create_comment("Comment 2", post.id, user.id)
    
    comments = db.get_comments_by_post(post.id)
    assert len(comments) == 2
    assert comment1 in comments
    assert comment2 in comments
