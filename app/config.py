# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # read .env into os.environ

# 12-Factor V: store config in environment
POSTGRES_URL = os.environ.get("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
SQL_ECHO     = os.environ.get("SQL_ECHO", "false").lower() in ("1", "true")

# For local development, you might want to override the database host
if os.environ.get("ENVIRONMENT") == "local":
    # Replace 'db' with 'localhost' for local development
    POSTGRES_URL = POSTGRES_URL.replace("@db:", "@localhost:")
