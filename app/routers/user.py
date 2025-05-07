from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, ultils
from ..database import engine, get_db

# Create a router
router = APIRouter(
    prefix="/users",
    tags=["Users"]  # Appears as a section in Swagger UI
)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    summary="Create a new user",
    response_description="The created user details"
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: User's email address (must be unique)
    - **password**: Plaintext password (will be hashed before storing)
    - **other fields**: Any additional fields defined in the `UserCreate` schema
    """
    # Hash the password before saving
    user.password = ultils.hash(user.password)

    created_user = models.User(**user.dict())
    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user

@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
    summary="Retrieve a user by ID",
    response_description="Details of the user with the given ID"
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by their unique ID.

    - **user_id**: The ID of the user to retrieve
    - **returns**: A user object if found, 404 error otherwise
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
