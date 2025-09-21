import uuid
from fastapi import HTTPException
from sqlmodel import Session, select

from backend.app.OAuth2 import get_password_hash
from backend.app.enums.emailTemplate import EmailTemplate
from .error import add_error, get_error_message
from .. import models, schemas, enums
from ..external_services.email_service import simple_send



error_keys = {
    "employee_roles_employee_id_fkey": "Employee does not exist",
    "employee_roles_pkey": "No Employee has this role",
    "ck_employees_valid_cnss_number": "CNSS number must be {8 digits}-{2 digits} and its mandatory for Cdi and Cdd",
    "employees_email_key": "Employee with this email already exists",
    "employees_pkey": "Employee with this id doesn't exist",
}

# confirm account
def get_confirmation_code(db: Session, code: str):
    stmt = select(models.AccountActivation).where(models.AccountActivation.token == code)
    act = db.exec(stmt).first() 
    return act

def add_confirmation_code(db: Session, db_employee: models.Employee):
    activation_code = models.AccountActivation(
            employee_id=db_employee.id, 
            email=db_employee.email, 
            status=enums.TokenStatus.Pending, 
            token=uuid.uuid1()
        )
    db.add(activation_code)

    return activation_code

# video 1h min 34:45c    
def edit_confirmation_code(db: Session, id: int, new_data: dict):
    db_token = db.get(models.AccountActivation, id)
    db_token.status = enums.TokenStatus.Used
    db.commit()
    return db_token

#reset pwd code 
def get_reset_code(db: Session, code: str):
    stmt = select(models.ResetPassword).where(models.ResetPassword.token == code)
    reset_code = db.exec(stmt).first() 
    return reset_code

def add_reset_code(db: Session, db_employee: models.Employee):
    reset_code = models.ResetPassword(
            employee_id=db_employee.id, 
            email=db_employee.email, 
            status=enums.TokenStatus.Pending, 
            token=uuid.uuid1()
        )
    db.add(reset_code)

    return reset_code

def edit_reset_code(db: Session, id: int, new_data: dict):
    db_token = db.get(models.ResetPassword, id)
    db_token.status = enums.TokenStatus.Used
    return db_token


#to refactor later !!!
def get_employee(db: Session, id: int):
    stmt = select(models.Employee).where(models.Employee.id == id)
    employee = db.exec(stmt).first()
    return employee

def get_employee_by_email(db: Session, email: str):
    stmt = select(models.Employee).where(models.Employee.email == email)
    employee = db.exec(stmt).first()
    return employee

# same shit !!
def edit_employee(db: Session, id: int, new_data: dict):
    db_employee = db.get(models.Employee, id)
    db_employee.account_status = new_data.get(models.Employee.account_status, db_employee.account_status)
    #1
    # db_employee = db.get(models.Employee, confirmation_code.employee_id)
    # db_employee.account_status = enums.AccountStatus.active

    #2
    # db_employee.account_status = new_data.get("account_status", db_employee.account_status)
    # edit_employee(db, confirmation_code.employee_id, {"account_status": enums.AccountStatus.active})


def get_employees(db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Employee).offset(skip).limit(limit)
    employees = db.exec(stmt).all()
    return employees

async def add(db: Session, employee: schemas.EmployeeCreate):
    try:
        #fix me later
        employee.password = get_password_hash(employee.password)
        employee_data = employee.model_dump()
        employee_data.pop('confirm_password', None)
        roles = employee_data.pop('roles', None)

        # add employee to the database
        db_employee = models.Employee(**employee_data) 
        db.add(db_employee)
        db.flush()
        db.refresh(db_employee)
      
        # add roles to the employee
        db.add_all([models.EmployeeRole(employee_id=db_employee.id, role=role) for role in roles])

        # add confirmation code 
        activation_code = add_confirmation_code(db, db_employee)


        # send confirmation email
        await simple_send([db_employee.email], {
                'name': db_employee.first_name,
                'code': activation_code.token,
                'psw': employee.password
            }, EmailTemplate.ConfirmAccount
        )
        db.commit()


    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text))
    
    return schemas.EmployeeOut(**db_employee.__dict__, roles=roles)

