from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, ultils, oauth2
from ..database import engine, get_db

# Create a router for vote-related operations
router = APIRouter(
    prefix="/vote",
    tags=["Votes"]  # Group in Swagger docs
)

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    summary="Vote or remove vote on a post",
    response_description="Confirmation message"
)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Cast or remove a vote on a post.

    - **post_id**: ID of the post to vote on
    - **dir**: Direction of vote  
      - `1` to vote  
      - `0` to remove vote

    This endpoint allows an authenticated user to either vote on a post or remove their vote.
    If a user tries to vote twice or remove a non-existent vote, appropriate errors are returned.
    """

    # Ensure the post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not exists"
        )

    # Check for existing vote
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    # If direction is 1, try to add a vote
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has already voted on this post"
            )

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully voted"}

    # If direction is 0, try to remove vote
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User has not voted on this post"
            )

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully removed vote"}
