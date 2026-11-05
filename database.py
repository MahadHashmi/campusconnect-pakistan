import os
import sys
import tempfile
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusconnect.db")

# Default Supabase pooler is paused after inactivity, so we default to resilient SQLite
# unless an active, verified DATABASE_URL is explicitly set.
RAW_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

engine = None
SessionLocal = None

def get_sqlite_engine():
    temp_dir = tempfile.gettempdir()
    db_file = os.path.join(temp_dir, "campus_connect_resilient.db")
    eng = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False}
    )
    return eng

# Check if valid Postgres URL provided and doesn't belong to the paused Supabase project
use_postgres = False
if RAW_DATABASE_URL and "pbyazfahuytyzxjkcluu" not in RAW_DATABASE_URL:
    try:
        url = RAW_DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            
        test_engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 2}
        )
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        use_postgres = True
        logger.info("Connected to remote PostgreSQL database.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}), falling back to SQLite.")
        engine = None

if engine is None:
    engine = get_sqlite_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
