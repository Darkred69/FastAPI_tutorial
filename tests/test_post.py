from app import schemas
import pytest

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