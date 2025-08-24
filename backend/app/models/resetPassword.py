from datetime import datetime
from ..enums.tokenStatus import TokenStatus
from sqlmodel import SQLModel, Field, func
from sqlalchemy import Column, ForeignKey, DateTime


class ResetPassword(SQLModel, table=True): 
    __tablename__ = "reset_password" 

    id: int = Field(default=None, primary_key=True)
    employee_id: int = Field(ForeignKey("employees.id"), index=True)
    email : str = Field(index=True, unique=True)
    token: str = Field(index=True, unique=True)
    status: TokenStatus = Field(index=True) 
    created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now(), index=True))