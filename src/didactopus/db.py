from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import load_settings

settings = load_settings()
engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
