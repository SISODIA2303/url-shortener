from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL) #creates the connection pool to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #factory that creates database sessions. Each request gets its own sessions
Base = declarative_base() #base class for all ORM classes

def get_db(): #dependency that provides a database session to the API endpoints. It ensures tha the session is properly closed after the request is processed.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()