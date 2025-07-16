# app/db.py
from sqlalchemy import create_engine, text
from app.config import POSTGRES_URL, SQL_ECHO

# echo=True will print all SQL; flip via SQL_ECHO
engine = create_engine(POSTGRES_URL, echo=SQL_ECHO, future=True)

def init_db() -> None:
    """Create prices table if it doesn't exist."""
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
