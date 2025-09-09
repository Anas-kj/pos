from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select
import uvicorn
import re
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

email_regex =  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
cnss_regex = r'^\d{8}-\d{2}$'
phone_number_regex = r'^\+?[0-9]{7,15}$'

mandatory_fields = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "password": "Password",
    "number": "Number",
    "contract_type": "Contract Type",
    "gender": "Gender",
    "roles": "Roles"
}

optional_fields = {
    "birth_date": "Birth Date",
    "address": "Address",
    "cnss_number": "Cnss Number",
    "phone_number": "Phone Number"
}

mandatory_with_condition = {
    "cnss_number": ("Cnss Number", lambda employee: isCdiOrCdd(employee))
}

possible_fields = {
    **mandatory_fields,
    **optional_fields,
    **mandatory_with_condition
}

unique_fields = {
    "email": models.Employee.email,
    "number": models.Employee.number,
}

options = [
    schemas.MatchyOption(mandatory_fields["first_name"], "first_name", True, enums.FieldType.string),
    schemas.MatchyOption(mandatory_fields["last_name"], "last_name", True, enums.FieldType.string),
    schemas.MatchyOption(mandatory_fields["email"], "email", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.regex, enums.Comparer.e, email_regex)
    ]),
    schemas.MatchyOption(mandatory_fields["password"], "password", True, enums.FieldType.string),
    schemas.MatchyOption(mandatory_fields["number"], "number", True, enums.FieldType.integer),
    schemas.MatchyOption(optional_fields["birth_date"], "birth_date", False, enums.FieldType.string),
    schemas.MatchyOption(optional_fields["address"], "address", False, enums.FieldType.string),
    schemas.MatchyOption(mandatory_with_condition["cnss_number"][0], "cnss_number", False, enums.FieldType.string),
    schemas.MatchyOption(mandatory_fields["contract_type"], "contract_type", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer._in, enums.ContractType.getPossibleValues())
    ]),
    schemas.MatchyOption(mandatory_fields["gender"], "gender", True, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer._in, enums.Gender.getPossibleValues())
    ]),
    schemas.MatchyOption(mandatory_fields["roles"], "roles", True, enums.FieldType.string),
    schemas.MatchyOption(optional_fields["phone_number"], "phone_number", False, enums.FieldType.string, [
        schemas.MatchyCondition(enums.ConditionProperty.value, enums.Comparer.e, phone_number_regex)
    ]),
]

def is_regex_matched(pattern, field):
    return field if re.match(pattern, field) else None

#fix me: move it later to a utils file
def is_valid_email(field: str):
    return field if is_regex_matched(email_regex, field) else None

def is_positive_int(field: str):
    try:
        res = int(field)
    except ValueError:
        return None
    return res if res >= 0 else None
    
def is_valid_date(field: str):
    try:
        return datetime.strptime(field, "%Y-%m-%d")
    except ValueError:
        return None

def isCdiOrCdd(employee):
    return employee["contract_type"].value  in [enums.ContractType.Cdi, enums.ContractType.Cdd] 

def is_valid_cnss_number(field):
    return field if is_regex_matched(cnss_regex, field) else None
    
def is_valid_phone_number(field: str):
    return field if is_regex_matched(phone_number_regex, field) else None

def are_valid_roles(field: str):
    res = []
    for role in field.split(","):
        role = role.strip()
        if enums.RoleType.is_valid_enum_value(role):
            res.append(role)
    return res if len(res) > 0 else None


fields_check = {
    "email": (lambda field: is_valid_email(field), "Wrong email format"),
    "gender": (lambda field: enums.Gender.is_valid_enum_value(field), f"Possible values are { enums.Gender.getPossibleValues() }"),
    "contract_type": (lambda  field: enums.ContractType.is_valid_enum_value(field), f"Possible values are { enums.ContractType.getPossibleValues() }"),
    "number": (lambda field: is_positive_int(field), "Number must be an integer"),
    "birth_date": (lambda field: is_valid_date(field), "Birth date must be in format YYYY-MM-DD"),
    "cnss_number": (lambda field: is_valid_cnss_number(field), "CNSS number must be {8 digits}-{2 digits} and Mandatory for Cdi and Cdd"),
    "phone_number": (lambda field: is_valid_phone_number(field), "Wrong phone number format"),
    "roles": (lambda field: are_valid_roles(field), f"Possible values are { enums.RoleType.getPossibleValues() }"),
    
}

def is_field_mandatory(employee, field):
    return field in mandatory_fields or (field in mandatory_with_condition and mandatory_with_condition[field][1](employee))

def validate_employee_data(employee):
    errors = []
    warnings = []
    wrong_cells = []
    employee_to_add = { field: cell.value for field, cell in employee.items() }

    for field in possible_fields:
        if field not in employee:
            if is_field_mandatory(employee, field):
                errors.append(f"{possible_fields[field]} is mandatory")
            continue

        cell = employee[field]
        employee_to_add[field] = employee_to_add[field].strip()

        if employee_to_add[field] == '':
            if is_field_mandatory(employee, field):
                msg = f"{possible_fields[field]} is mandatory"
                errors.append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(msg, cell.rowIndex, cell.colIndex))
            else:
                employee_to_add[field] = None
        elif field in fields_check:
            converted_val = fields_check[field][0](employee_to_add[field])
            if converted_val is None:
                msg = fields_check[field][1]
                (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(msg, cell.rowIndex, cell.colIndex))
            else:
                employee_to_add[field] = converted_val
    return (errors, warnings, wrong_cells, employee_to_add)
            

def valid_employees_data_and_upload(employees: list, force_upload: bool, db: Session = Depends(get_db)):
    errors = []
    warnings = []
    wrong_cells = []
    employee_to_add = []

    for line, employee in enumerate(employees):
        emp_errors, emp_warnings, emp_wrong_cells, emp = validate_employee_data(employee)
        if emp_errors:
            msg = ('\n').join(emp_errors)
            errors.append(f"\nLine {line + 1}: \n{msg}")
        if emp_warnings:
            msg = ('\n').join(emp_warnings)
            warnings.append(f"\nLine {line + 1}: \n{msg}")
        if emp_wrong_cells:
            wrong_cells.extend(emp_wrong_cells)
        
        employee_to_add.append(emp)
   
    for fields in unique_fields:
        values = set()
        for line, employee in enumerate(employees):
            cell = employee.get(fields)
            val = cell.value.strip()
            if val == '':
                continue

            if val in values:
                msg = f"{possible_fields[fields]} must be unique."
                
                wrong_cells.append(schemas.MatchyWrongCell(msg, cell.rowIndex, cell.colIndex))

            else:
                values.add(val)

            stmt = select(models.Employee).where(unique_fields[fields].in_(values))
            duplicated_vals = db.exec(stmt).all()
            if duplicated_vals:
                msg = f"{possible_fields[fields]} must be unique. {(', ').join(duplicated_vals)} already exists in the database."
                (errors if is_field_mandatory(employee, fields) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(msg, cell.rowIndex, cell.colIndex))
    
     
    if errors or (warnings and not force_upload):
        return schemas.ImportResponse(
            errors=('\n').join(errors),
            warnings=('\n').join(warnings),
            wrongCells=wrong_cells
        )
    




@app.post("employee/import")
def importEmployess():
    pass

@app.get("/employees/possibleImportFields", response_model=schemas.ImportPossibleFields)
def getPossibleFields(db: Session = Depends(get_db)):
    return schemas.ImportPossibleFields(
        possible_fields=options,
    )

@app.post('employees/csv')
def upload(entry: schemas.MatchyUploadEntry, db: Session = Depends(get_db)):
    employees = entry.lines
    if not employees:
        raise HTTPException(status_code=400, detail="No employees to import")
    
    missing_mandatory_fields = set(mandatory_fields.keys()) - set(employees[0].keys())
    if missing_mandatory_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing mandatory fields: {', '.join([display for field, display in missing_mandatory_fields.items()])}"
        ) 

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)