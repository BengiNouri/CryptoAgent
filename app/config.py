# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # read .env into os.environ

# 12-Factor V: store config in environment
POSTGRES_URL = os.environ["POSTGRES_URL"]
SQL_ECHO     = os.environ.get("SQL_ECHO", "false").lower() in ("1", "true")
