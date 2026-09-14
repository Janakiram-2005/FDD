import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH26188 - AI-Based Fake Identity & Document Screening System"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "document_screening_db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
