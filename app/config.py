from pydantic_settings import BaseSettings

# Schema for Environment variables



class Settings(BaseSettings):
    # For database
    database_hostname: str = "localhost"
    database_port: str = '5432'
    database_password: str = 'root'
    database_username: str = "postgres"
    database_name: str
    # For tokenization
    secret_key: str
    algorithm: str
    access_token_expire_minutes: str

    class Config:
        env_file=".env"
settings = Settings()  