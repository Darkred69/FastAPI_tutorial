from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, ultils # import from the models.py
from ..database import engine, get_db # import the engine from the database.py

# Create a router
router = APIRouter(
    prefix= "/users",
    tags = ["Users"] # for documentation
)

# Create a user
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password - user.password
    user.password = ultils.hash(user.password)
    
    # Query to create a post - ORM
    created_user = models.User(**user.dict()) # Create the new user
    db.add(created_user) # Add it to the database
    db.commit() # Commit the transaction to save the changes to database Postgres
    db.refresh(created_user) # Refresh the database to retrive the new post

    return created_user

# Get a specific user using id
@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = "User not found")
    
    return user