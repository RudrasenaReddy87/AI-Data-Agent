from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///users.db"  # Fallback to local SQLite database

try:
    engine = create_engine(DATABASE_URL)
    # Test the connection
    with engine.connect() as conn:
        pass
except Exception as e:
    print(f"Database connection failed: {e}, falling back to local SQLite")
    DATABASE_URL = "sqlite:///users.db"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
