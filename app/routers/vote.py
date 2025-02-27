from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, ultils, oauth2 # import from the models.py
from ..database import engine, get_db # import the engine from the database.py

# Create a router
router = APIRouter(
    prefix = "/vote",
    tags=["Votes"] # For documentation
)

@router.post("/", status_code = status.HTTP_201_CREATED)
def vote(vote:schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # Check if post exsits
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post not exsits")

    # Find the user's vote in the Vote database
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id) 
    found_vote = vote_query.first()

    # The user want to vote
    if (vote.dir == 1):
        # Checked if that vote exsit, yes than return Exception
        if found_vote:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "User has already vote on this post")
        
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id) # Vote the post
        db.add(new_vote) # Add the data
        db.commit() # Commit to database
        return {"message": "Succesfully voted"}
    # The user want to remove vote
    else:
        # Checked if that vote exsits, no than return Exception
        if not found_vote: 
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "User never vote this post")
        
        vote_query.delete(synchronize_session = False) # Delete the exsiting vote
        db.commit() # Commit to database
        return {"message": "Succesfully removed vote"}