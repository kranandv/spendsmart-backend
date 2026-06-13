from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Connection
DATABASE_URL = os.getenv("DATABASE_URL")  # Render gives this directly

engine = create_engine(
    DATABASE_URL,
    echo=False,                    # Set True during development
    pool_pre_ping=True,            # Good for Render
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Pgadmin_123@localhost/TodoApplicationDatabase"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mysql_123@localhost:3306/SpendSmartDatabase"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()