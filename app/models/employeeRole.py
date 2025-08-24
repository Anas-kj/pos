from sqlmodel import SQLModel, Field, Relationship
from app.models.employee import Employee
from sqlalchemy import ForeignKey
from app.enums import RoleType


class EmployeeRole(SQLModel, table=True): 
    __tablename__ = "employee_roles" 

    id: int = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id", index=True)
    employee: Employee = Relationship()
    role: RoleType = Field(index=True)