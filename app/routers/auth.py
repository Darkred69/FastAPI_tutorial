from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, ultils, oauth2

# Define an API router with a "Authentication" tag for automatic Swagger grouping
router = APIRouter(
    tags=["Authentication"]
)

# Login endpoint
@router.post("/login", response_model=schemas.Token, summary="Authenticate a user and return a JWT token", response_description="JWT access token with token type")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user using their email and password.

    - **username**: Email address (used as username field by OAuth2 spec)
    - **password**: User's password
    - **Returns**: JWT access token and token type if credentials are valid.

    This endpoint validates the user's credentials and returns an access token,
    which can be used to authorize requests to protected endpoints.
    """
    
    # Fetch the user from the database using email (OAuth2 uses "username" for form field)
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    # Raise error if user not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    # Verify the provided password against the stored hash
    if not ultils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    # Create JWT access token with user_id encoded
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    # Return the token in the format expected by OAuth2 clients
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
