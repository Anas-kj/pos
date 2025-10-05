from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import func, update
from sqlmodel import Session, select

from backend.app import crud
from backend.app.OAuth2 import get_curr_employee
from backend.app.crud.employee import add_employee, get_all_emp
from backend.app.database import get_session

from .. import schemas, models, enums
from ..external_services import email_service
from ..dependencies import DbDep, paginationParams, currentEmployee

import datetime
import uuid
import re

app = APIRouter(
    prefix="/employee",
    tags=["Employee"],
)

error_keys = {
    "employee_roles_employee_id_fkey": "Employee does not exist",
    "employee_roles_pkey": "No Employee has this role",
    "ck_employees_valid_cnss_number": "CNSS number must be {8 digits}-{2 digits} and its mandatory for Cdi and Cdd",
    "employees_email_key": "Employee with this email already exists",
    "employees_pkey": "Employee with this id doesn't exist",
}

@app.post("/", response_model=schemas.EmployeeOut)
async def add(employee: schemas.EmployeeCreate, db: DbDep): #, current_employee: currentEmployee):
    try:
        db_employee = await add_employee(db=db, employee=employee)
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys))

    return schemas.EmployeeOut(**db_employee.__dict__)
    

@app.put("/{id}", response_model=schemas.BaseOut)
async def edit_employee(id: int, entry: schemas.EmployeeEdit, db: DbDep):
    try:
        stmt = (
            update(models.Employee)
            .where(models.Employee.id == id)
            .values(**entry.model_dump())
            .execution_options(synchronize_session=False)
        )
        await db.exec(stmt)
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys)(text))
    
    return schemas.BaseOut(
        detail="Employee updated successfully", 
        status_code=status.HTTP_200_OK
    )


# Having getting roles problem
@app.get("/all", response_model=schemas.EmployeesOut)
def get_all(db: DbDep, pagination_param: paginationParams, name_substr: str = None):
    try:
        employees, total_records, total_pages = get_all_emp(db, pagination_param, name_substr)
    except Exception as e:
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys)(text))
    return schemas.EmployeesOut(
        detail="Employees retrieved successfully",
        status_code=status.HTTP_200_OK,
        page_number=pagination_param.page_number,
        page_size=pagination_param.page_size,
        total_pages=total_pages,
        total_records=total_records,
        list=[schemas.EmployeeOut(**employee.__dict__) for employee in employees]
    )

email_regex =  r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
cnss_regex = r'^\d{8}-\d{2}$'
phone_number_regex = r'^\+?[0-9]{7,15}$'

mandatory_fields = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
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
    schemas.MatchyOption(display_value=mandatory_fields["first_name"], value="first_name", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["last_name"], value="last_name", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["email"], value="email", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex, comparer=enums.Comparer.e, value=email_regex)
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["number"], value="number", mandatory=True, type=enums.FieldType.integer),
    schemas.MatchyOption(display_value=optional_fields["birth_date"], value="birth_date", mandatory=False, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=optional_fields["address"], value="address", mandatory=False, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_with_condition["cnss_number"][0], value="cnss_number", mandatory=False, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex, comparer=enums.Comparer.e, value=cnss_regex)
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["contract_type"], value="contract_type", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value, comparer=enums.Comparer._in, value=enums.ContractType.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["gender"], value="gender", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value, comparer=enums.Comparer._in, value=enums.Gender.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["roles"], value="roles", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=optional_fields["phone_number"], value="phone_number", mandatory=False, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value, comparer=enums.Comparer.e, value=phone_number_regex)
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
                msg = f"{possible_fields[field][0]} is mandatory"
                errors.append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
            else:
                employee_to_add[field] = None
        elif field in fields_check:
            converted_val = fields_check[field][0](employee_to_add[field])
            if converted_val is None:
                msg = fields_check[field][1]
                (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
            else:
                employee_to_add[field] = converted_val
    return (errors, warnings, wrong_cells, employee_to_add)
            
def  valid_employees_data_and_upload(employees: list, force_upload: bool, backgroundTasks: BackgroundTasks, db: DbDep):
    try:
        errors = []
        warnings = []
        wrong_cells = []
        employee_to_add = []
        roles_per_email = {}

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
            
            roles_per_email[emp.get('email')] = emp.pop('employee_roles')
            employee_to_add.append(models.Employee(**emp))
    
        for field in unique_fields:
            values = set()
            for line, employee in enumerate(employees):
                cell = employee.get(field)
                val = cell.value.strip()
                if val == '':
                    continue

                if val in values:
                    msg = f"{possible_fields[field]} must be unique."
                    
                    wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))

                else:
                    values.add(val)

            stmt = select(models.Employee).where(unique_fields[field].in_(values))
            duplicated_vals = db.exec(stmt).all()
            duplicated_vals = {[str(val[0]) for val in duplicated_vals]}
            if duplicated_vals:
                msg = f"{possible_fields[field]} must be unique. {(', ').join(duplicated_vals)} already exists in the database."
                (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                for employee in employees:
                    cell = employee.get(field)
                    val = cell.value.strip()

                    if val in duplicated_vals:
                        wrong_cells.append(schemas.MatchyWrongCell(message=f"{possible_fields[field]} must be unique. {val} already exists in the database.", rowIndex=cell.rowIndex, colIndex=cell.colIndex))
        
        
        if errors or (warnings and not force_upload):
            return schemas.ImportResponse(
                detail="File has some errors",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=('\n').join(errors),
                warnings=('\n').join(warnings),
                wrong_cells=wrong_cells
            )
        
        db.add_all(employee_to_add)
        db.flush()

        # case 1: lost order
        employee_roles = []
        for emp in employee_to_add:
            for role in roles_per_email[emp.email]:
                employee_roles.append(models.EmployeeRole(employee_id=emp.id, role=role))

        db.add_all(employee_roles)
        db.flush()

        activation_codes_to_add = []
        email_data = []
        for emp in employee_to_add:
            token = uuid.uuid1()
            activation_code = models.AccountActivation(
                employee_id=emp.id, 
                email=emp.email, 
                status=enums.TokenStatus.Pending, 
                token=token
            )
            activation_codes_to_add.append(activation_code)
            email_data.append(([emp.email], {
                "name": emp.first_name,
                "code": token,
                "psw": emp.password,
            }))

        db.add_all(activation_codes_to_add)

        for email_datum in email_data:
            backgroundTasks.add_task(email_service.simple_send, email_datum[0], email_datum[1])
        
        db.commit()

    except Exception as e:
        db.rollback() 
        text = str(e)
        add_error(text, db)

        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys)(text))

    return schemas.ImportResponse(
        detail="File imported successfully",
        status_code=status.HTTP_201_CREATED
    )

def add_error(text, db: Session):
    try:
        db.add(models.Error(text=text))
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")

def get_error_message(error_message, error_keys):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key]
    return "Something went wrong"


@app.post("/employee/import")
def importEmployess():
    pass

@app.get("/possibleImportFields", response_model=schemas.ImportPossibleFields)
def getPossibleFields(db: DbDep):
    return schemas.ImportPossibleFields(
        possible_fields=options,
    )

@app.post('/test')
async def upload(entry: schemas.MatchyUploadEntry, backgroundTasks: BackgroundTasks ,db: DbDep):
    employees = entry.lines
    if not employees:
        raise HTTPException(status_code=400, detail="No employees to import")
    
    missing_mandatory_fields = set(mandatory_fields.keys()) - set(employees[0].keys())
    if missing_mandatory_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing mandatory fields: {', '.join([mandatory_fields[field] for field in missing_mandatory_fields])}"
        ) 
    
    return valid_employees_data_and_upload(employees, backgroundTasks, entry.forceUpload, db)