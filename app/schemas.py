from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint

# Schema for the request body - Pydantic Model
# All variables in schema must be the same with in models

# User schema
class User(BaseModel):
    email:EmailStr
    password:str

# User create schema for create a user
class UserCreate(User):
    pass

# User schema for returning user
class UserOut(BaseModel):
    id:int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True 

# # User schema for login use in Login function
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str




# Schema for Post
class PostBase(BaseModel):
    title: str # The title of the post
    content: str # The content of the post
    published: bool = True # To publish the post or not, default to True
    # rating: Optional[int] = None # The rating of the post, optional integer, default to None

# Schema for CreatePost input
class PostCreate(PostBase):
    pass

# Schema for output Post
class Post(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: UserOut
    # Config for Pydantic to return the data as a dictionary
    class Config:
        from_attributes = True

# Schema for OutPut Post but modify with votes
class PostOut(BaseModel):
    post: Post
    votes: int
    # Config for Pydantic to return the data as a dictionary
    class Config:
        from_attributes = True

# Schema to input Votes in Vote router
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # type: ignore


# Schema of an expected Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema of TokenData, uses when get user data from token
class TokenData(BaseModel):
    id: Optional[str] = None