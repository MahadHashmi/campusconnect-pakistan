import os
import sys
import tempfile
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("campusconnect.db")

SUPABASE_PG8000_URL = "postgresql+pg8000://postgres.pbyazfahuytyzxjkcluu:MyCampusPass2026!@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
RAW_DATABASE_URL = os.getenv("DATABASE_URL", SUPABASE_PG8000_URL).strip()

def get_sqlite_engine():
    temp_dir = tempfile.gettempdir()
    db_file = os.path.join(temp_dir, "campus_connect_resilient.db")
    eng = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False}
    )
    return eng

engine = None

try:
    url = RAW_DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+pg8000://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+pg8000://", 1)
    elif "psycopg2" in url:
        url = url.replace("postgresql+psycopg2://", "postgresql+pg8000://", 1)

    test_engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
    with test_engine.connect() as conn:
        pass
    engine = test_engine
    logger.info("Connected to remote cloud PostgreSQL database successfully!")
except Exception as e:
    logger.warning(f"Cloud PostgreSQL ping failed ({e}). Falling back to local SQLite.")
    engine = get_sqlite_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
