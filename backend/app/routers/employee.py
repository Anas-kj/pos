import uuid
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

def get_user_by_email(db: Session, email: str):
    stmt = select(models.Employee).where(models.Employee.email == email)
    employee = db.exec(stmt).first()
    return employee

def get_all (db: Session, skip: int = 0, limit: int = 10):
    stmt = select(models.Employee).offset(skip).limit(limit)
    employees = db.exec(stmt).all()
    return employees

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
        print(e)
    

    return schemas.EmployeeOut(**db_employee.__dict__, roles=roles)

