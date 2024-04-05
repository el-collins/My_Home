from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    secret_key: str = "SECRET_KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()

# Additional configuration settings would go here...