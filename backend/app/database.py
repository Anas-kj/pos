from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from .config import settings


database_url = f"postgresql://{settings.database_username}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
