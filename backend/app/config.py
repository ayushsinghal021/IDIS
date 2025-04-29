from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, Literal
import os


class Settings(BaseSettings):
    """Application settings"""
    # General
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    
    # File storage
    upload_folder: str = "./data/documents"
    processed_folder: str = "./data/processed"
    vector_folder: str = "./data/vectors"
    
    # OCR settings
    ocr_engine: Literal["tesseract", "paddleocr"] = "tesseract"
    tesseract_path: Optional[str] = None
    
    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_dimension: int = 384
    
    # LLM settings
    llm_provider: Literal["openai", "ollama", "huggingface"] = "openai"
    openai_api_key: Optional[str] = None
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # Security
    api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()