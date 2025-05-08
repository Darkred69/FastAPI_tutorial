from passlib.context import CryptContext

# Initialize the password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: A bcrypt-hashed version of the password.
    """
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.

    Args:
        plain_password (str): The user-entered plain text password.
        hashed_password (str): The stored hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
