from sqlmodel import SQLModel, Field, Relationship
from .employee import Employee
from datetime import datetime, UTC


class Error(SQLModel, table=True): 
    __tablename__ = "errors" 

    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(index=True)
    created_at: datetime = Field(default=datetime.now(UTC), index=True)

  
