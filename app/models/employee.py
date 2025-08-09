from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field
from app.enums import ContractType, Gender, AccountStatus
from datetime import datetime, UTC


class Employee(SQLModel, table=True): 
    __tablename__ = "employees" 

    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    badge_number: int = Field(default=None, index=True)
    email : str = Field(index=True, unique=True)
    password: str = Field(index=True)
    number: str = Field(default=None, index=True)
    birth_date: str | None = Field(default=None, index=True)
    address: str | None = Field(default=None, index=True)
    cnss_number: str = Field(default=None, index=True)
    contract_type: ContractType = Field(default=None, index=True)
    gender : Gender = Field(default=None, index=True)
    Account_status: AccountStatus = Field(default=AccountStatus.inactive)
    phone_number : str = Field(default=None, index=True)
    created_at: datetime = Field(default=datetime.now(UTC), index=True)

    __table_args__ = (
        CheckConstraint(
            "(contract_type IN ('Cdi', 'Cdd') AND cnss_number IS NOT NULL AND cnss_number ~ '^\\d{8}-\\d{2}$') OR (contract_type IN ('Sivp', 'Apprenti') AND (cnss_number IS NULL OR cnss_number ~ '^\\d{8}-\\d{2}$'))",
            name='ck_employees_valid_cnss_number'
        ),
    )
