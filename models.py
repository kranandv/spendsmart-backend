from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String)
    phonenumber = Column(String)
    is_active = Column(Boolean, default=True)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    category = Column(String)
    description = Column(String)
    date = Column(Date)
    mode=Column(String)
    etype = Column(String)
    notes = Column(String)
    created_at = Column(DateTime)