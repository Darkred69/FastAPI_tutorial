# Fixture for creating a post with 1 vote
import pytest
from app import models



# Test vote on vote.py with user 1
def test_vote(authorized_client, test_posts):
    data = {"post_id": test_posts[0].id, "dir": 1}
    res = authorized_client.post("/vote/", json = data)
    assert res.status_code == 201
    assert res.json().get("message") == "Succesfully voted"

# Test vote on already vote post with user 1
def test_vote_twice(authorized_client, test_posts, vote_post):
    data = {"post_id": test_posts[0].id, "dir": 1} # 
    res = authorized_client.post("/vote/", json = data)
    assert res.status_code == 409
    assert res.json().get("detail") == "User has already vote on this post"

# Test un-vote on already vote post with user 1
def test_unvote(authorized_client, test_posts, vote_post):
    data = {"post_id": test_posts[0].id, "dir": 0} # Un-vote post 1
    res = authorized_client.post("/vote/", json = data)
    assert res.status_code == 201
    assert res.json().get("message") == "Succesfully removed vote"

# Test vote on already vote post with user 1
def test_unvote_twice(authorized_client, test_posts ):
    data = {"post_id": test_posts[1].id, "dir": 0} # Post 2 never been voted 
    res = authorized_client.post("/vote/", json = data)
    assert res.status_code == 409
    assert res.json().get("detail") == "User never vote this post"

def test_vote_non_exsist_post(authorized_client, test_posts ):
    data = {"post_id": 3232323, "dir": 0} # Non exsist post
    res = authorized_client.post("/vote/", json = data)
    assert res.status_code == 404
    assert res.json().get("detail") == "Post not exsits"

def test_vote_unauthorized(client, test_posts):
    data = {"post_id": test_posts[1].id, "dir": 0} 
    res = client.post("/vote/", json = data) # Client is not authorized

    assert res.status_code == 401
    assert res.json().get('detail') == 'Not authenticated'