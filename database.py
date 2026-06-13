from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Pgadmin_123@localhost/TodoApplicationDatabase"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mysql_123@localhost:3306/SpendSmartDatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()