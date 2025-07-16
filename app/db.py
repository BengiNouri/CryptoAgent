# app/db.py
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command
import os
from app.config import POSTGRES_URL, SQL_ECHO

# echo=True will print all SQL; flip via SQL_ECHO
engine = create_engine(POSTGRES_URL, echo=SQL_ECHO, future=True)

def init_db() -> None:
    """Run Alembic migrations to ensure database is up to date."""
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    alembic_cfg_path = os.path.join(project_root, "alembic.ini")
    
    if os.path.exists(alembic_cfg_path):
        alembic_cfg = Config(alembic_cfg_path)
        command.upgrade(alembic_cfg, "head")
    else:
        # Fallback to raw DDL if alembic.ini not found (for backwards compatibility)
        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS prices (
                  id          SERIAL PRIMARY KEY,
                  coin_id     TEXT,
                  symbol      TEXT,
                  date        DATE,
                  price       NUMERIC,
                  market_cap  NUMERIC,
                  volume      NUMERIC
                )
            """))
