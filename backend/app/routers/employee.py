import uuid
from fastapi import HTTPException
from sqlmodel import Session, select
from .. import models, schemas, enums
from ..routers.mail_service import simple_send

def get_confirmation_code(db: Session, code: str):
    stmt = select(models.AccountActivation).where(models.AccountActivation.token == code)
    act = db.exec(stmt).first() 
    return act

def get_user(db: Session, id: int):
    stmt = select(models.Employee).where(models.Employee.id == id)
    employee = db.exec(stmt).first()
    return employee

def get_all (db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Employee).offset(skip).limit(limit)
    employees = db.exec(stmt).all()
    return employees

error_keys = {
    "employee_roles_employee_id_fkey": "Employee does not exist",
    "employee_roles_pkey": "No Employee has this role",
    "ck_employees_valid_cnss_number": "CNSS number must be {8 digits}-{2 digits} and its mandatory for Cdi and Cdd",
    "employees_email_key": "Employee with this email already exists",
    "employees_pkey": "Employee with this id doesn't exist",
}

def get_error_message(error_message):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key]
    return "Something went wrong"

def add_error(text, db: Session):
    try:
        db.add(models.Error(text=text))
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")
    

async def add(db: Session, employee: schemas.EmployeeCreate):
    try:
        #fix me later
        fake_hashed_password = employee.password + "notreallyhashed"
        employee_data = employee.model_dump()
        employee_data.pop('confirm_password', None)
        roles = employee_data.pop('roles', None)
        employee_data['password'] = fake_hashed_password

        # add employee to the database
        db_employee = models.Employee(**employee_data) 
        db.add(db_employee)
        db.flush()
        db.refresh(db_employee)
      

        # add roles to the employee
        db.add_all([models.EmployeeRole(employee_id=db_employee.id, role=role) for role in roles])


        # add activation code 
        activation_code = models.AccountActivation(
            employee_id=db_employee.id, 
            email=db_employee.email, 
            status=enums.TokenStatus.Pending, 
            token=uuid.uuid1()
        )

        db.add(activation_code)


        # send confirmation email
        await simple_send([db_employee.email], {
            "code": activation_code.token,
        })
        db.commit()


    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)

        raise HTTPException(status_code=500, detail=get_error_message(text))
    

    return schemas.EmployeeOut(**db_employee.__dict__, roles=roles)

