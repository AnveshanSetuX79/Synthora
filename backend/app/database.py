"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/localai_leads"
)

# Create SQLAlchemy engine with optimized connection pool for high concurrency
# Configured to handle 100+ concurrent users
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Disable SQL logging for performance
    pool_size=30,  # Base pool size (increased from 20)
    max_overflow=70,  # Overflow connections (total 100 connections)
    pool_timeout=30,  # Wait 30 seconds for connection
    pool_recycle=1800  # Recycle connections after 30 minutes
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
