import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("knowiix.database")

Base = declarative_base()

engine = None
SessionLocal = None

def init_db_engine():
    global engine, SessionLocal
    try:
        # Create MySQL engine with pooling and healthcheck
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info(f"Connected to MySQL database at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
    except Exception as e:
        logger.warning(f"Could not connect to MySQL: {e}. Falling back to in-memory store.")
        engine = None
        SessionLocal = None

# Initialize on module load
init_db_engine()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for yielding DB sessions per request.
    """
    if SessionLocal is None:
        init_db_engine()

    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_mysql_connection() -> dict:
    """
    Utility function to test MySQL connection status.
    """
    try:
        if engine is None:
            init_db_engine()
        if engine is None:
            return {"connected": False, "error": "Engine not initialized"}
            
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            return {"connected": result == 1, "host": settings.MYSQL_HOST, "database": settings.MYSQL_DATABASE}
    except Exception as e:
        return {"connected": False, "error": str(e)}
