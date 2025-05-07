from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas, ultils, oauth2
from ..database import engine, get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut], summary="Get all posts", response_description="List of all posts with vote counts")
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    """
    Retrieve all posts with pagination, optional search filter, and vote counts.

    - **limit**: Max number of posts to return (default: 10)
    - **skip**: Number of posts to skip for pagination
    - **search**: Filter posts by title containing this string
    - **returns**: List of posts with vote counts
    """
    post_query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    posts = [
        schemas.PostOut(
            post=schemas.Post.model_validate(post),
            votes=votes
        )
        for post, votes in post_query
    ]
    return posts

@router.get("/{post_id}", response_model=schemas.PostOut, summary="Get a post by ID", response_description="Post details with vote count")
def get_post(
    post_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Retrieve a single post by its ID.

    - **post_id**: The ID of the post to retrieve
    - **returns**: Post details and vote count if found, 404 error if not
    """
    post_query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post, votes = post_query
    return schemas.PostOut(
        post=schemas.Post.model_validate(post),
        votes=votes
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post, summary="Create a new post", response_description="The created post")
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Create a new post.

    - **title**: Title of the post
    - **content**: Content body
    - **published**: Publish status (boolean)
    - **returns**: The newly created post
    """
    created_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a post", response_description="Post deleted successfully")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Delete a post by its ID.

    - **Requires ownership**: Only the post creator can delete it
    - **returns**: 204 No Content if successful, 404/403 if not
    """
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{post_id}", response_model=schemas.Post, summary="Update a post", response_description="The updated post")
def update_post(
    post_id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    """
    Update a post by its ID.

    - **Requires ownership**: Only the post creator can update it
    - **returns**: The updated post object if successful
    """
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
