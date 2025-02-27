# This fille help testing without import any fixtures, conftest is package specific
# fixture is a function that runs before the test 
# scope = module: runs every time it test another test_.py
# scope = session: runs once every time uses pytest
# scope = function: runs every function
# Fixture for setting connection with database
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app import schemas
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
# Database set up for testing
# Database config
username = settings.database_username # Default postgres
password = settings.database_password # Default root
ip_host = settings.database_hostname # Default localhost
port = settings.database_port # Default 5432
database = settings.database_name # Database name

# SQLALCHEMY_DATABASE_URL - this is for testing
SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{ip_host}:{port}/{database}_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session maker - This is for testing
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture() 
def session():
    Base.metadata.drop_all(bind=engine) # Drop all tables after running our code
    Base.metadata.create_all(bind=engine) # Create all tables before running our code
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# fixture to set up a client
@pytest.fixture()
def client(session):
    def override_get_db(): # Override for testing
        try:
            yield session
        finally:
            session.close()
    # Override get_db with override_get_db for testing
    app.dependency_overrides[get_db] = override_get_db
    # Specify the TestClient
    yield TestClient(app) # uses with yield, which we can specify what runs before and what runs after the yield,
    # run after our test finishes 


# Fixture that always create 1 user joe@gmail.com with password: 123456 for testing other functions involving login
@pytest.fixture
def test_user(client):
    user_data = {'email':'joe@gmail.com', 'password': '123456'}
    res = client.post("/users/", json = user_data)
    assert res.status_code == 201

    user = res.json() # Convert the response into a dict
    user['password'] = user_data['password'] # Add password to the return user since our schemas for this don't return password
    return user # Return a user that we can uses in login

# Fixture returns a token for post operations
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

# Fixture that modifies the client with authorization
@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client



# Fixture for creating example posts
@pytest.fixture
def test_posts(session, test_user):
    post_data = [{"title": "Post1", "content": "Content1", "owner_id":test_user['id']}, 
                 {"title": "Post2", "content": "Content2", "owner_id":test_user['id']}, 
                 {"title": "Post3", "content": "Content3", "owner_id":test_user['id']}]
    # Small function the create post 
    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, post_data) # Map the dict into list
    posts = list(post_map) # Turn the map into list
    session.add_all(posts)
    session.commit()
    return session.query(models.Post).all()