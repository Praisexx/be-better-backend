import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Meta Ads AI Analyzer"
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/metaads_analyzer')

    # OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')

    # Web Search APIs (optional - for enhanced business search)
    TAVILY_API_KEY: str = os.getenv('TAVILY_API_KEY', '')
    SERPAPI_KEY: str = os.getenv('SERPAPI_KEY', '')

    # Email
    RESEND_API_KEY: str = os.getenv('RESEND_API_KEY', '')
    FROM_EMAIL: str = os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')

    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Upload settings
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', 209715200))  # 200MB
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')

    # CORS
    FRONTEND_URL: str = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings()
