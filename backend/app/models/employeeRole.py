from sqlmodel import SQLModel, Field, Relationship
from ..enums import RoleType


class EmployeeRole(SQLModel, table=True): 
    __tablename__ = "employee_roles" 

    id: int = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id", index=True)
    role: RoleType = Field(index=True)