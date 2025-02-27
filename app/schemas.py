from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint

# Schema for the request body - Pydantic Model
# All variables in schema must be the same with in models
class User(BaseModel):
    email:EmailStr
    password:str

class UserCreate(User):
    pass

class UserOut(BaseModel):
    id:int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True 

class UserLogin(BaseModel):
    email: EmailStr
    password: str





class PostBase(BaseModel):
    title: str # The title of the post
    content: str # The content of the post
    published: bool = True # To publish the post or not, default to True
    # rating: Optional[int] = None # The rating of the post, optional integer, default to None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: UserOut
    # Config for Pydantic to return the data as a dictionary
    class Config:
        from_attributes = True


class PostOut(BaseModel):
    post: Post
    votes: int
    # Config for Pydantic to return the data as a dictionary
    class Config:
        from_attributes = True


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # type: ignore



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None