import jwt
from app.config import settings
from app import schemas
import pytest

    

# Testing root path in main.py
def test_root(client):
    res = client.get("/")
    print(res.json().get('message'))
    assert res.json().get('message') == "Welcome to my API!"
    assert res.status_code == 200

# Testing create user from user.py
def test_create_user(client):
    res = client.post("/users/", json = {'email':'lay@gmail.com', 'password': '123456'})
    new_user = schemas.UserOut(**res.json()) # Uses Pydantic model to check for validation of response
    assert new_user.email == "lay@gmail.com"
    assert res.status_code == 201

# Testing for login
def test_login_user(client, test_user):
    res = client.post("/login", data = {'username': test_user['email'], 'password':test_user['password']})
    login_res = schemas.Token(**res.json()) # Assure the return is Token Schema
    # Decode the token to test the id 
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms = [settings.algorithm]) # Decode the token
    id = payload.get("user_id") # Get the ID from the token, payload is a dict, and user_id is what we added when create token
    
    assert id == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200

# Testing for incorrect login
@pytest.mark.parametrize("email, password, status_code",[
                         ("joe@gmail.com", "fsdfsdf", 403),
                         ('wrong@gmail.com', "123456", 403),
                         (None, "123456", 403),
                         ("joe@gmail.com", None, 403)
                         ])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data = {'username': email, 'password':password}) # wrong password
    assert res.status_code == status_code
    assert res.json().get('detail') == "Invalid Credentials"