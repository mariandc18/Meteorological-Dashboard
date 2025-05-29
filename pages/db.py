from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.storage.config import DATABASE_URL

print("DATABASE_URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db_session():
    return SessionLocal()