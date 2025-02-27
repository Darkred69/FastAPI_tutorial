from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import time

# # Connect to database - RAW SQL
# while True:
#     try :
#         conn = psycopg2.connect(host = 'localhost', database = 'FastAPI', user = 'postgres', password = 'root', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Connected to the database")
#         break
#     except Exception as e:
#         print(e)
#         time.sleep(2)

# Database config
username = settings.database_username # Default postgres
password = settings.database_password # Default root
ip_host = settings.database_hostname # Default localhost
port = settings.database_port # Default 5432
database = settings.database_name # Database name

# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/host>/<database-name>"
SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{ip_host}:{port}/{database}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base
Base = declarative_base() # Create a base class

# Dependency to get the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()