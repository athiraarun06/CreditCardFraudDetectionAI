import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("fraud_detection")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "fraud.db")
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL) or DEFAULT_SQLITE_URL

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
        logger.info(f"Database engine created for {DATABASE_URL.split('@')[-1]}")
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def init_db():
    from app.models import user, customer, merchant, transaction, prediction, alert, model_metrics  # noqa
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables verified/created.")


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
