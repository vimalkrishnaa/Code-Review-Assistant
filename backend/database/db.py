from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database configuration
DATABASE_URL = "sqlite:///./reviews.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def init_db():
    """Initialize database - create all tables if they don't exist"""
    try:
        # Import all models here to ensure they are registered with Base
        from models.db_models import ReviewRecord
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def get_session() -> Session:
    """Get database session - use as context manager or dependency"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_db_session() -> Session:
    """Get a database session for direct use"""
    return SessionLocal()

def close_session(session: Session):
    """Close a database session"""
    session.close()
