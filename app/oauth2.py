from fastapi import Depends
from jose import JWTError
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from . import schemas, database, models
from .config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login") #Pass the URL of the Login route

# Tokenization requirements
SECRETE_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Create a new access token
def create_access_token(data: dict):
    to_encode = data.copy() # Ensure no data is being change
    expire = datetime.utcnow() + timedelta(minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire}) # Add the expire time of the token to the data payload
    encoded_jwt = jwt.encode(to_encode, SECRETE_KEY, algorithm = ALGORITHM) # Create the token
    return encoded_jwt

# Verify the access token
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms = [ALGORITHM]) # Decode the token
        id = payload.get("user_id") # Get the ID from the token, payload is a dict, and user_id is what we added when create token

        if id is None: # Check if Id exsits
            raise credentials_exception
        
        token_data = schemas.TokenData(id = str(id)) # Check if the id schema is correct
    
    except JWTError:
        raise credentials_exception
    
    return token_data

# Get current user
def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate credentials", headers = {"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user