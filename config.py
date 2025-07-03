# config.py
import os

class Config:
    # App settings
    APP_NAME = "ATS CV Scorer - Data Professionals"
    APP_ICON = "🎯"
    
    # File upload settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc']
    
    # Scoring weights
    KEYWORD_WEIGHT = 0.4
    FORMAT_WEIGHT = 0.35
    CONTENT_WEIGHT = 0.25
    
    # Database (şimdilik SQLite)
    DATABASE_URL = "sqlite:///ats_scorer.db"