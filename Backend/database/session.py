from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./farm_it.db"

# Create engine with check_same_thread=False for FastAPI compatibility
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Database dependency for FastAPI.
    Yields a database session that automatically closes after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
