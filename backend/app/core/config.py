import os
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Metrology Compliance Scanner"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "legal-metrology-secret-key-for-jwt-signing-siih2026-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/legal_metrology_db"
    
    # File Storage
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")
    REPORT_OUTPUT_DIR: str = os.path.join(os.getcwd(), "generated_reports")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8000",
    ]

    # Default Seeds
    FIRST_SUPERUSER_EMAIL: str = "admin@legalmetrology.gov.in"
    FIRST_SUPERUSER_PASSWORD: str = "AdminPassword@123"
    FIRST_INSPECTOR_EMAIL: str = "inspector.mumbai@legalmetrology.gov.in"
    FIRST_INSPECTOR_PASSWORD: str = "InspectorPassword@123"

    # OCR Configuration
    TESSERACT_CMD_PATH: Optional[str] = None
    OCR_CONFIDENCE_THRESHOLD: float = 0.60
    OCR_DISAGREEMENT_SIMILARITY_THRESHOLD: float = 0.80
    OCR_IOU_MATCHING_THRESHOLD: float = 0.30

    # External Public APIs & AI Integration (from public-apis/public-apis & LLM Providers)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    OPEN_FOOD_FACTS_API_URL: str = "https://world.openfoodfacts.org"
    POSTAL_PINCODE_API_URL: str = "https://api.postalpincode.in"
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest"
    OPEN_METEO_API_URL: str = "https://api.open-meteo.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
