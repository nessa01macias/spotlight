"""
Database initialization and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from .database import Base

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spotlight.db")

# Create engine
# For SQLite: check_same_thread=False allows FastAPI to use it across threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database - create all tables
    """
    print(f"Initializing database at: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def get_db() -> Session:
    """
    Dependency to get database session
    Use in FastAPI endpoints with Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_direct() -> Session:
    """
    Get database session directly (for scripts, not endpoints)
    Remember to close it when done!
    """
    return SessionLocal()
