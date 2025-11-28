"""Database configuration for VocalMetric backend."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# SQLite database stored in the backend directory
DB_PATH = Path(__file__).resolve().parent / "vocalmetric.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# echo=False for quieter logs in development; adjust as needed
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
