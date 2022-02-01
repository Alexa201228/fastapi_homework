from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import databases

SQL_DATABASE_URL = 'sqlite:///./sqlite_db.db'

database = databases.Database(SQL_DATABASE_URL)
db_engine = create_engine(SQL_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()
