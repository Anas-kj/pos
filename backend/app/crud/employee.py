from fastapi import HTTPException
from sqlalchemy import func, update
from sqlmodel import Session, select

from backend.app import enums
from backend.app.OAuth2 import get_password_hash
from backend.app.crud.auth import add_confirmation_code
from backend.app.dependencies import PaginationParams
from backend.app.enums.emailTemplate import EmailTemplate
from .. import models, schemas
from ..external_services.email_service import simple_send



error_keys = {
    "employee_roles_employee_id_fkey": "Employee does not exist",
    "employee_roles_pkey": "No Employee has this role",
    "ck_employees_valid_cnss_number": "CNSS number must be {8 digits}-{2 digits} and its mandatory for Cdi and Cdd",
    "employees_email_key": "Employee with this email already exists",
    "employees_pkey": "Employee with this id doesn't exist",
}

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


def div_ceil(nominator, denominator):
    full_pages = nominator // denominator
    additional_page = 1 if nominator % denominator > 0 else 0
    return full_pages + additional_page

def get_all_emp(db: Session, pagination_param: PaginationParams, name_substr):
    query = select(models.Employee)
    
    if name_substr:
        query = query.where(func.lower(func.concat(models.Employee.first_name, ' ', models.Employee.last_name)).contains(func.lower(name_substr)))

    total_records = db.scalar(select(func.count()).select_from(query.subquery()))
    total_pages = div_ceil(total_records, pagination_param.page_size)
    stmt = (
        query
        .limit(pagination_param.page_size)
        .offset((pagination_param.page_number - 1) * pagination_param.page_size)
    )
    employees = db.scalars(stmt).all()
    return (employees, total_records, total_pages)



async def add_employee(db: Session, employee: schemas.EmployeeCreate):
 
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
    activation_code = add_confirmation_code(db, db_employee.id, db_employee.email)
    # send confirmation email
    await simple_send([db_employee.email], {
            'name': db_employee.first_name,
            'code': activation_code.token,
            'psw': employee.password
        }, EmailTemplate.ConfirmAccount
    )
    db.commit()
    return db_employee


async def edit_employee_password(db: Session, id: int, entry: schemas.EmployeeEdit):
    employee = db.get(models.Employee, id)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found") 
    
    fields_to_update = entry.model_dump()
    for field in ['password', 'email', 'confirm_password', 'actual_password', 'roles']:
        fields_to_update.pop(field)
    
    if employee.email != entry.email:
        if not entry.actual_password or get_password_hash(entry.actual_password) != employee.password:
            raise HTTPException(status_code=400, detail="Actual password is incorrect")
        
        fields_to_update[models.Employee.email] = entry.email
        fields_to_update[models.Employee.account_status] = enums.AccountStatus.inactive

    if entry.password and get_password_hash(entry.password) != employee.password:
        if entry.password != entry.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if not entry.actual_password or get_password_hash(entry.actual_password) != employee.password:
            raise HTTPException(status_code=400, detail="Actual password is incorrect")
        
        fields_to_update[models.Employee.password] = get_password_hash(entry.password)
        
    db.exec(
            update(models.Employee)
            .where(models.Employee.id == id)
            .values(**fields_to_update)
            .execution_options(synchronize_session=False)
        )
    
    if models.Employee.email in fields_to_update:
        activation_code = add_confirmation_code(db, employee.id, fields_to_update[models.Employee.email])
        await simple_send([employee.email], {
                'name': employee.first_name,
                'code': activation_code.token,
            }, EmailTemplate.ConfirmAccount
        )

    db.commit()    
