from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session
import uvicorn
from . import schemas, models, enums
from .database import create_db_and_tables, get_session
from .routers import employee as crud, mail_service

async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Dependency
def get_db():
    yield from get_session()

@app.get("/")
async def root():
    return await mail_service.simple_send(["tisoha2149@litepax.com"], {
        "first_name" : "Fred",
        "last_name" : "Flintstone",
    })

@app.post("/employee/", response_model=schemas.EmployeeOut)
async def create_user(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    db_employee = crud.get_user_by_email(db, employee.email)
    if employee.password != employee.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.add(db=db, employee=employee) 

@app.patch("/employee", response_model=schemas.BaseOut)
def confirm_account(confirmAccountInput : schemas.ConfirmAccount, db: Session = Depends(get_db)):
    confirmation_code = crud.get_confirmation_code(db, confirmAccountInput.confirmation_code)

    if not confirmation_code:
        raise HTTPException(status_code=404, detail="Confirmation code not found")
    
    if confirmation_code.status == enums.TokenStatus.Used:
        raise HTTPException(status_code=400, detail="Confirmation code already used")
    
    diff = (datetime.now() - confirmation_code.created_at).seconds
    if diff > 3600:
        raise HTTPException(status_code=400, detail="Confirmation code expired")
    
    db_employee = db.get(models.Employee, confirmation_code.employee_id)
    db_employee.account_status = enums.AccountStatus.active
    db.commit()

    db_token = db.get(models.AccountActivation, confirmation_code.id)
    db_token.status = enums.TokenStatus.Used
    db.commit()

    return schemas.BaseOut(
        detail="Account confirmed successfully",
        status_code=status.HTTP_200_OK,
    )

options = [
    schemas.MatchyOption("First Name", "first_name", True, enums.FieldType.string),
    schemas.MatchyOption("Last Name", "last_name", True, enums.FieldType.string),
    schemas.MatchyOption("Email", "email", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.regex, enums.Comparer.e, "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    ]),
    schemas.MatchyOption("Password", "password", True, enums.FieldType.string),
    schemas.MatchyOption("Number", "number", True, enums.FieldType.integer),
    schemas.MatchyOption("Birth Date", "birth_date", False, enums.FieldType.string),
    schemas.MatchyOption("Address", "address", False, enums.FieldType.string),
    schemas.MatchyOption("Cnss Number", "cnss_number", False, enums.FieldType.string),
    schemas.MatchyOption("Contract Type", "contract_type", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer._in, enums.ContractType.getPossibleValues())
    ]),
    schemas.MatchyOption("Gender", "gender", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer._in, enums.Gender.getPossibleValues())
    ]),
    schemas.MatchyOption("Roles", "roles", True, enums.FieldType.string),
    schemas.MatchyOption("Phone Number", "phone_number", False, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer.e, "^\\+?[0-9]{7,15}$")
    ]),
]

@app.post("employee/import")
def importEmployess():
    pass

@app.get("/employees/possibleImportFields", response_model=schemas.ImportPossibleFields)
def getPossibleFields(db: Session = Depends(get_db)):
    return schemas.ImportPossibleFields(
        possible_fields=options,
    )

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)