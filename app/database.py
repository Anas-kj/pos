from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine
from app.config import settings


database_url = f"postgresql://{settings.database_username}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)