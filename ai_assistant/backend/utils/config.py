# backend/utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# API Configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OpenAI Configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database Configurations
DATABASE_URL = os.getenv("DATABASE_URL")

# Git Configurations
DEFAULT_REPO_PATH = os.getenv("DEFAULT_REPO_PATH", ".")

# File Storage Configurations
FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "./user_files")

# Vector DB Configurations
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data")

# Logging Configurations
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")