# Run code on cmd uvicorn app.main:app --reload
from fastapi import FastAPI

from .routers import post, user, auth, vote # Import post and user routers
from . import models
from .database import engine # import the engine from the database.py
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine) # Create the tables in the database automatically can be remove if have alembic
# Create a FastAPI Instance
app = FastAPI()

origins = ["*"] # Setting for everyone

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Welcome to my API!"}


