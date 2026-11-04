"""
Database Configuration and Session Management for QuantumVault.
Production-hardened MySQL connection pool and session factory.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure production MySQL connection pooling parameters
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def check_db_connection():
    """Verify MySQL database connectivity without altering schema."""
    try:
        with engine.connect() as conn:
            pass
    except Exception as e:
        logger.warning(f"MySQL database connectivity warning: {e}")


# Verify connection on module load
check_db_connection()


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
