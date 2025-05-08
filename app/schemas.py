from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint

# ------------------------------------------------------------
# Pydantic Schemas for Data Validation and Serialization
# Used for request bodies and response models in FastAPI
# ------------------------------------------------------------

# ------------------------
# User-Related Schemas
# ------------------------

class User(BaseModel):
    """
    Schema for user credentials input (e.g., during registration or login).
    """
    email: EmailStr
    password: str

class UserCreate(User):
    """
    Schema for creating a new user. Inherits from User.
    """
    pass

class UserOut(BaseModel):
    """
    Schema for user output (e.g., when returning user info).
    """
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Enables ORM-to-Pydantic conversion


# ------------------------
# Post-Related Schemas
# ------------------------

class PostBase(BaseModel):
    """
    Base schema for post-related fields shared by other post schemas.
    """
    title: str  # Title of the post
    content: str  # Content/body of the post
    published: bool = True  # Default to published

class PostCreate(PostBase):
    """
    Schema for creating a new post. Inherits from PostBase.
    """
    pass

class Post(PostBase):
    """
    Schema for post output including additional fields like ID and owner.
    """
    id: int
    owner_id: int
    created_at: datetime
    owner: UserOut  # Nested user schema for owner details

    class Config:
        from_attributes = True

class PostOut(BaseModel):
    """
    Schema for outputting a post along with its vote count.
    """
    post: Post
    votes: int

    class Config:
        from_attributes = True


# ------------------------
# Vote-Related Schemas
# ------------------------

class Vote(BaseModel):
    """
    Schema for voting on posts.
    
    Attributes:
        post_id (int): ID of the post being voted on.
        dir (int): Direction of the vote, 1 to vote, 0 to unvote.
    """
    post_id: int
    dir: conint(le=1)  # Constraint: vote direction must be 0 or 1


# ------------------------
# Token-Related Schemas
# ------------------------

class Token(BaseModel):
    """
    Schema representing the JWT token returned after successful authentication.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema representing token payload data for extracting the user ID.
    """
    id: Optional[str] = None
