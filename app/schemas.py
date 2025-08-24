from datetime import datetime, date
from typing import List
from sqlmodel import SQLModel, Field  
from .enums import ContractType, Gender, AccountStatus, RoleType
from datetime import datetime


class OurBaseModel(SQLModel):
    class Config:
        from_attributes = True

class EmployeeBase(OurBaseModel):
    first_name: str
    last_name: str
    email : str
    number: int
    birth_date: date | None = None
    address: str | None = None
    cnss_number: str | None = None
    contract_type: ContractType
    gender : Gender 
    roles: List[RoleType]
    phone_number : str | None = None


class EmployeeCreate(EmployeeBase):
    password: str | None = None
    confirm_password: str | None = None

class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime | None = None