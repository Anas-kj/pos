from socket import EAI_SERVICE
from sqlmodel import Session, select
from .. import models, schemas
from ..routers.mail_service import simple_send


def get_user(db: Session, id: int):
    stmt = select(models.Employee).where(models.Employee.id == id)
    employee = db.exec(stmt).first()
    return employee

def get_user_by_email(db: Session, email: str):
    stmt = select(models.Employee).where(models.Employee.email == email)
    employee = db.exec(stmt).first()
    return employee

def get_all (db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Employee).offset(skip).limit(limit)
    employees = db.exec(stmt).all()
    return employees

async def add(db: Session, employee: schemas.EmployeeCreate):
    #fix me later
    fake_hashed_password = employee.password + "notreallyhashed"
    employee_data = employee.model_dump()
    employee_data.pop('confirm_password', None)
    roles = employee_data.pop('roles', None)
    employee_data['password'] = fake_hashed_password

    # add employee to the database
    db_employee = models.Employee(**employee_data) 
    db.add(db_employee)
    db.commit() # commit vs flush
    db.refresh(db_employee)

    # add roles to the employee
    for role in roles:
        db_role = models.EmployeeRole(employee_id=db_employee.id, role=role)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)


    # send confirmation email
    await simple_send([employee_data['email']])
    

    return schemas.EmployeeOut.model_validate(db_employee.__dict__)

