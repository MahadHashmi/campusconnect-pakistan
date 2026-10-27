import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.pbyazfahuytyzxjkcluu:MyCampusPass2026!@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

# Ensure SQLAlchemy uses psycopg2 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
        connect_args={"connect_timeout": 4}
    )
    # Quick probe to verify if Supabase is active
    with engine.connect() as probe:
        pass
except Exception as e:
    # If Supabase free tier is paused due to inactivity, fall back to SQLite so the app NEVER crashes
    db_path = os.path.join(os.path.dirname(__file__), "campus_connect.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    try:
        import models
        models.Base.metadata.create_all(bind=engine)
    except Exception:
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
