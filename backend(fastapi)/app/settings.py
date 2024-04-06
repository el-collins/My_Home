from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # mongodb_url: str = "mongodb://localhost:27017"
    secret_key: str = "1c6b3c0e9fbd0fb47fe187b1ee7f8f62ed481366d34f5ca3e667d39accd4b51f"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()