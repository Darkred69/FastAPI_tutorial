from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas, ultils, oauth2 # import from the models.py
from ..database import engine, get_db # import the engine from the database.py

# Create a router
router = APIRouter(
    prefix = "/posts",
    tags=["Posts"] # For documentation
)

# Get all posts
@router.get("/",response_model = List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""): 
    # The post query

    post_query = (db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True)
        .group_by(models.Post.id) # Perfrom a Left Outer Join to get all post with and without votes
        .filter(models.Post.title.contains(search)) # Query Parameter
        .limit(limit) # Query Parameter
        .offset(skip) # Query Parameter
        .all()
    ) 
    # print(post_query) # print query by remove .all()
    
    ## Query to get all the posts - RAW SQL
    # cursor.execute("SELECT * FROM posts") # Execute the query
    # my_posts = cursor.fetchall() # Return the result of the query

    # Convert SQLAlchemy objects to Pydantic models fit PostOut
    posts = [
        schemas.PostOut(
            post=schemas.Post.model_validate(post),  # ✅ Converts Post correctly
            votes=votes  # ✅ Passes votes separately
        )
        for post, votes in post_query
    ]
    return posts

# Get one specific post
@router.get("/{post_id}", response_model = schemas.PostOut)
def get_post(post_id: int, response: Response, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)): #Auto convert the post_id to an integer
    
    # # Query to get the post - RAW SQL
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (str(post_id))) 
    # post = cursor.fetchone()

    # Query to get the post - ORM
    post_query = (db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True)
        .group_by(models.Post.id) # Perfrom a Left Outer Join to get all post with and without votes
        .filter(models.Post.id == post_id)
        .first()
    )

    # Check if post exists
    if not post_query: 
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": "Post not found"}
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = "Post not found")

    # Convert SQLAlchemy objects to Pydantic models fit PostOut
    post, votes = post_query # Since only 1 return, we don't need to unpack with for like above
    posts = schemas.PostOut( # remove the [] since there is only 1 return
                post=schemas.Post.model_validate(post),  # ✅ Converts Post correctly
                votes=votes  # ✅ Passes votes separately
                )
    
    return posts 

# Create a new post
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    # # Query to create a post - RAW SQL
    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ", (post.title, post.content, post.publish)) # Execute the query
    # created_post = cursor.fetchone() # Return the result of the query
    # conn.commit() # Commit the transaction to save the changes to database Postgres
    
    # Query to create a post - ORM
    
    created_post = models.Post(owner_id = current_user.id, **post.dict()) # Create the new post, **post.dict() replace the post.title, post.content, post.publish
    db.add(created_post) # Add it to the database
    db.commit() # Commit the transaction to save the changes to database Postgres
    db.refresh(created_post) # Refresh the database to retrive the new post

    # # Display votes when return
    # post_query = (db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
    #     .join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True)
    #     .group_by(models.Post.id) # Perfrom a Left Outer Join to get all post with and without votes
    #     .filter(models.Post.id == created_post.id)
    #     .first()
    # ) 
    # post,votes = post_query
    # posts = schemas.PostOut(
    #         post=schemas.Post.model_validate(post),  # ✅ Converts Post correctly
    #         votes=votes  # ✅ Passes votes separately
    #     )

    return created_post


# Delete a post
@router.delete("/{post_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):

    # # Query to delete the post - RAW SQL
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(post_id))) # Execute the query, add the returning to return the deleted post
    # post = cursor.fetchone() # Return the result that will be deleted
    # conn.commit() # Saved the changes to the database

    # Query to delete the post - ORM
    post_query = db.query(models.Post).filter(models.Post.id == post_id)# Get the post
    post = post_query.first()
    
    # Check if post exists
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = "Post not found")

    # Check the owner of the post
    if post.owner_id != current_user.id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "Not authorize")
    
    post_query.delete(synchronize_session = False) # Delete the post
    db.commit() # Commit the transaction to save the changes to database Postgres

    return Response(status_code = status.HTTP_204_NO_CONTENT)

# Update a post using PUT
@router.put("/{post_id}", response_model = schemas.Post)
def update_post(post_id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):

    # # Query to get the post - RAW SQL
    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (post.title, post.content, post.publish, str(post_id))) # Execute the query
    # post = cursor.fetchone() # Return the result of the query
    # conn.commit() # Commit the transaction to save the changes to database Postgres

    # Query to get the post - ORM
    post_query = db.query(models.Post).filter(models.Post.id == post_id) # Get the post
    post = post_query.first()

    # Check if post exists
    if not post: 
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = "Post not found")
    
    # Check the owner of the post
    if post.owner_id != current_user.id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "Not authorize")

    post_query.update(updated_post.dict(), synchronize_session = False) # Update the post
    db.commit() # Commit the transaction to save the changes to database Postgres
    return post_query.first() # Return the updated post
