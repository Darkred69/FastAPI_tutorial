from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # JSON Web Token implementation
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from . import schemas, database, models
from .config import settings

# ---------------------------------------------------
# OAuth2 and JWT Authentication Utility for FastAPI
# ---------------------------------------------------

# Define OAuth2 password bearer scheme with token URL (login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Load token-related environment settings
SECRETE_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    """
    Generates a new JWT access token.

    Args:
        data (dict): Data to encode into the JWT payload.

    Returns:
        str: Encoded JWT token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # Add expiration to payload

    encoded_jwt = jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Decodes and validates a JWT access token.

    Args:
        token (str): The JWT token string.
        credentials_exception (HTTPException): Exception to raise if validation fails.

    Returns:
        TokenData: A Pydantic schema containing the user ID from token.
    """
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")

        if id is None:
            raise credentials_exception

        return schemas.TokenData(id=str(id))

    except JWTError:
        raise credentials_exception

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    """
    Dependency to get the current user based on the JWT token.

    Args:
        token (str): Bearer token extracted from the request.
        db (Session): SQLAlchemy database session.

    Returns:
        models.User: The user associated with the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user
