from datetime import datetime, date
from typing import List, Optional, Dict
from sqlmodel import SQLModel

from backend.app.enums.matchyComparer import Comparer
from .enums import ContractType, Gender, RoleType, ConditionProperty, FieldType
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

class ConfirmAccount(OurBaseModel):
    confirmation_code: str

class BaseOut(OurBaseModel):
    detail: str 
    status_code: int

class MatchyCondition(OurBaseModel):
    property: ConditionProperty
    comparer: Optional[Comparer] = None
    value: int | float | str | List[int]
    custom_fail_message: Optional[str] = None


class MatchyOption(OurBaseModel):
    display_value: str
    value: Optional[str] = None
    mandatory: Optional[bool] = False
    type: FieldType
    conditions: Optional[List[MatchyCondition]] = []
    

class ImportPossibleFields(OurBaseModel):
    possible_fields: List[MatchyOption] = []
    

class MatchyCell(OurBaseModel):
    value: str
    rowIndex: int
    colIndex: int

class MatchyUploadEntry(OurBaseModel):
    lines: List[Dict[str, MatchyCell]]

class MatchyWrongCell(OurBaseModel):
    message: str
    rowIndex: int
    colIndex: int

class ImportResponse(OurBaseModel):
    errors: str
    warnings: str
    wrongCells: list[MatchyWrongCell]