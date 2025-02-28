from sqlalchemy import func
from app import schemas
import pytest
from app import models

# Test the function of getting all post in post.py
def test_get_all_post(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200

# Test unauthorized user get all post
def test_unauthorized_user_get_all_post(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

# Test unauthorized user get one post
def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

# Test getting a non-exsisting post
def test_one_post_not_exsit(authorized_client,test_posts):
    res = authorized_client.get("/posts/8888") # id don't exsits
    assert res.status_code == 404

# Test getting one post
def test_get_one_post(authorized_client,test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    desire_post = schemas.PostOut(**res.json()) # Validate the post response schema
    assert desire_post.post.id == test_posts[0].id
    assert desire_post.post.content == test_posts[0].content

# Test creating a new post
@pytest.mark.parametrize("title, content, published", [
    ("New 1", "Content new 1", True),
    ("New 2", "Content new 2", True),
    ("New 3", "Content new 3", False)
])
def test_create_post(authorized_client, test_user, title, content, published):
    res = authorized_client.post("/posts/", json = {"title":title , "content": content, "published": published})
    created_post = schemas.Post(**res.json()) # Validate the post response schema, note newly create post don't have votes
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']

# Test creating post but published = NULL
def test_create_post_published_isnull(authorized_client, test_user):
    res = authorized_client.post("/posts/", json = {"title":"title4" , "content": "content4"})
    created_post = schemas.Post(**res.json()) # Validate the post response schema, note newly create post don't have votes
    assert res.status_code == 201
    assert created_post.title == "title4"
    assert created_post.content == "content4"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']

# Test unauthorized user create one post
def test_unauthorized_user_create_post(client):
    res = client.post("/posts/", json = {"title":"title4" , "content": "content4"})
    assert res.status_code == 401

# Test unauthorized delete post
def test_unauthorized_user_delete_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

# Test delete post function from post.py
def test_delete_post(authorized_client, test_user, test_posts, session):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    remain = session.query(func.count(models.Post.id)).first() # Count the remaining posts
    assert len(test_posts) == remain[0] + 1 # Test that the number of posts in db if it decreases
    assert res.status_code == 204 

# Test delete non-exsist post
def test_delete_nonexsis_post(authorized_client, test_user, test_posts, session):
    post_id = 74837483 # non-exsist post id
    res = authorized_client.delete(f"/posts/{post_id}")
    remain = session.query(func.count(models.Post.id)).first() # Count the remaining posts
    assert len(test_posts) == remain[0]  # Test that the number of posts in db doesn't decrease
    assert res.status_code == 404 

# Test delete other user post
def test_delete_other_user_post(authorized_client, test_user, test_posts, session):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}") #This post is not own by authorized client
    remain = session.query(func.count(models.Post.id)).first() # Count the remaining posts
    assert len(test_posts) == remain[0] # Test that the number of posts in db doesn't decrease
    assert res.status_code == 403

# Test update post from post.py
def test_update_post(authorized_client, test_user, test_posts, session):
    data = {"title": "Update Post1", "content": " Update Content1", "published": False}
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json = data) 
    updated_post = schemas.Post(**res.json()) # Check validation schemas
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']
    assert updated_post.published == data['published']

# Test update non exsist post
def test_update_non_exist_post(authorized_client, test_user, test_posts, session):
    data = {"title": "Update Post1", "content": " Update Content1", "published": False}
    post_id = 3233453 # non exsisting id
    res = authorized_client.put(f"/posts/{post_id}", json = data)  # Non exsisting post

    assert res.status_code == 404
    assert res.json().get('detail') == "Post not found"

# Test update not authorize post
def test_update_not_authorize_post(authorized_client, test_user, test_posts, session):
    data = {"title": "Update Post1", "content": " Update Content1", "published": False}
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json = data)  # not authorize post

    assert res.status_code == 403
    assert res.json().get('detail') == 'Not authorize'

# Test unauthorized user update
def test_update_unauthorized(client, test_user, test_posts, session):
    data = {"title": "Update Post1", "content": " Update Content1", "published": False}
    post_id = test_posts[0].id # non exsisting id
    res = client.put(f"/posts/{post_id}", json = data)  # Non exsisting post

    assert res.status_code == 401
    assert res.json().get('detail') == 'Not authenticated'