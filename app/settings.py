from pydantic_settings import BaseSettings # type: ignore
import os # Import the os module to interact with the operating system
from dotenv import load_dotenv # type: ignore # Import the load_dotenv function from the dotenv module to load environment variables from a.env file

load_dotenv() # Load environment variables from the.env file
class Settings(BaseSettings):
    # The MongoDB connection URL. This is currently set to the default local MongoDB instance.
    # mongodb_url: str = "mongodb://localhost:27017"

    # The secret key used for generating and verifying access tokens.
    secret_key: str = "1c6b3c0e9fbd0fb47fe187b1ee7f8f62ed481366d34f5ca3e667d39accd4b51f"

    # The algorithm used for generating and verifying access tokens. This is currently set to HS256.
    algorithm: str = "HS256"

    # The number of minutes before an access token expires.
    # 8 days access token expire minutes
    access_token_expire_minutes: int = 60 * 24 * 8
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")
    APP_BASE_URL: str = "http://127.0.0.1:8000"
    SECRET_KEY: str  = "cabcf753bc8f56d01e6183fa379e35601118288d148726ee"
    FORGET_PASSWORD_URL: str  = 'api/v1/auth/forget-password'
    RESET_PASSWORD_URL: str  = 'api/v1/auth/reset-password'
    MAIL_FROM_NAME="MyHome",

settings = Settings()