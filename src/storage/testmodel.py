from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class TestModel(Base):
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value=Column(Integer)
