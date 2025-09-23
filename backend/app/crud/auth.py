import uuid
from sqlalchemy import select
from sqlmodel import Session
from backend.app import enums, models


# confirm account
def get_confirmation_code(db: Session, code: str):
    stmt = select(models.AccountActivation).where(models.AccountActivation.token == code)
    act = db.exec(stmt).first() 
    return act[0]

def add_confirmation_code(db: Session, id: int, email: str):
    activation_code = models.AccountActivation(
            employee_id=id, 
            email=email, 
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
    return reset_code[0]

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