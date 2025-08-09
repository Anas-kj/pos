from datetime import datetime
from sqlmodel import SQLModel, Field, func
from app.enums.tokenStatus import TokenStatus
from sqlalchemy import ForeignKey, DateTime, Column


class AccountActivation(SQLModel, table=True): 
    __tablename__ = "account_activation" 

    id: int = Field(default=None, primary_key=True)
    employee_id: int = Field(ForeignKey("employees.id"), index=True)
    token : str = Field(index=True, unique=True)
    status : TokenStatus = Field(index=True)
    created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now(), index=True))