from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict

from backend.app.enums.matchyComparer import Comparer
from .enums import ContractType, Gender, RoleType, ConditionProperty, FieldType
from datetime import datetime


class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True

class BaseOut(OurBaseModel):
    detail: str 
    status_code: int

class PagedResponse(BaseOut):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int


class EmployeeBase(OurBaseModel):
    first_name: str
    last_name: str
    email : str
    number: int
    birth_date: date | None = None
    address: str | None = None
    cnss_number: str | None = None
    contract_type: ContractType | None = None
    gender : Gender 
    roles: List[RoleType]
    phone_number : str | None = None


class EmployeeCreate(EmployeeBase):
    password: str | None = None
    confirm_password: str | None = None

class EmployeeEdit(EmployeeCreate):
    actual_password: str | None = None

class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime | None = None

class EmployeesOut(PagedResponse):
    list: List[EmployeeOut]

class ConfirmAccount(OurBaseModel):
    confirmation_code: str

class ForgetPassword(OurBaseModel):
    email: EmailStr

class ResetPassword(OurBaseModel):
    reset_code: str
    psw: str
    confirm_psw: str

class MatchyCondition(OurBaseModel):
    property: ConditionProperty
    comparer: Optional[Comparer] = None
    value: int | float | str | List[str]
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
    forceUpload: Optional[bool] = False

class MatchyWrongCell(OurBaseModel):
    message: str
    rowIndex: int
    colIndex: int

class ImportResponse(BaseOut):
    errors: Optional[str] = None
    warnings: Optional[str] = None
    wrong_cells: Optional[list[MatchyWrongCell]] = [] 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

