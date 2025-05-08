from pydantic_settings import BaseSettings

# ----------------------------------------------------
# Configuration Schema for Environment Variables
# ----------------------------------------------------

class Settings(BaseSettings):
    """
    Configuration class to load environment variables using Pydantic.

    This class reads values from a `.env` file or environment and makes them
    accessible via `settings.<variable>`.

    Attributes:
        database_hostname (str): Hostname of the PostgreSQL database.
        database_port (str): Port number for the database connection.
        database_username (str): Username for the PostgreSQL database.
        database_password (str): Password for the PostgreSQL database.
        database_name (str): Name of the PostgreSQL database.
        secret_key (str): Secret key used for JWT encoding.
        algorithm (str): Algorithm used for JWT (e.g., HS256).
        access_token_expire_minutes (str): Expiry duration (in minutes) for access tokens.
    """

    # Database configuration
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_username: str = "postgres"
    database_password: str = "root"
    database_name: str

    # JWT and token settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: str

    class Config:
        """
        Pydantic configuration class.

        Specifies that environment variables should be read from a `.env` file.
        """
        env_file = ".env"

# Instantiate settings to be imported throughout the application
settings = Settings()
