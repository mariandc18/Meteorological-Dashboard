from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value=Column(Integer)

class UserRole(enum.Enum):
    guest = 'guest'
    user = 'user'
    admin = 'admin'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cookie_uid = Column(String(36), unique=True, nullable=False)
    email = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, nullable=False, default='guest')  # Como texto para SQLite
    analysis_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    last_access = Column(DateTime, nullable=True)