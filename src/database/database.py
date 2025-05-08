import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# load from .env
load_dotenv()

# Read the database URL from the environment variable
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

# Create the database engine (connection)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used to talk to the DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for defining models
Base = declarative_base()


# 🔹 Function to initialize DB and create tables
def init_db():
    from src.database import models 
    models.Base.metadata.create_all(bind=engine)