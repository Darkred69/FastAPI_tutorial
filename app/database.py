from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# -----------------------------------------
# Database Configuration using SQLAlchemy
# -----------------------------------------

# Load database settings from environment variables or .env file
username = settings.database_username  # Default: "postgres"
password = settings.database_password  # Default: "root"
ip_host = settings.database_hostname   # Default: "localhost"
port = settings.database_port          # Default: "5432"
database = settings.database_name      # Name of the target database

# Construct the SQLAlchemy database URL
# Format: postgresql://<username>:<password>@<host>:<port>/<database>
SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{ip_host}:{port}/{database}"

# Create a database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "SessionLocal" class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declaring ORM models (i.e., tables)
Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session.

    Yields:
        db (Session): SQLAlchemy session object.
    Ensures that the session is closed after the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
