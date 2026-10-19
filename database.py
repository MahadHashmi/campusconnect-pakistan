import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get Database URL from .env, with a Supabase production fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.pbyazfahuytyzxjkcluu:MyCampusPass2026!@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

# Supabase provides URLs starting with 'postgresql://' or 'postgres://'.
# Ensure SQLAlchemy uses psycopg2 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency that provides a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
