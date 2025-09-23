
from datetime import timedelta
import datetime
from fastapi import APIRouter, HTTPException, status
from ..schemas import Token
from backend.app import enums, models, schemas
from backend.app.OAuth2 import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_employee, create_access_token, get_password_hash
from backend.app.crud.auth import get_confirmation_code, add_reset_code, get_reset_code
from backend.app.crud.employee import get_employee_by_email
from backend.app.crud.error import add_error, get_error_message
from backend.app.dependencies import DbDep, formDataDep
from backend.app.enums.emailTemplate import EmailTemplate
from backend.app.external_services.email_service import simple_send

app = APIRouter(
    tags=["Authentication"]
)

error_keys = {}

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: DbDep, form_data: formDataDep):
    try:
        employee = authenticate_employee(db, form_data.username, form_data.password)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": employee.email}, expires_delta=access_token_expires
        )
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=text)
    
    return Token(access_token=access_token, token_type="bearer")


@app.patch("/confirmAccount", response_model=schemas.BaseOut)
def confirm_account(confirmAccountInput : schemas.ConfirmAccount, db: DbDep):
    try:
        confirmation_code = get_confirmation_code(db, confirmAccountInput.confirmation_code)

        if not confirmation_code:
            raise HTTPException(status_code=404, detail="Confirmation code not found")
        
        if confirmation_code.status == enums.TokenStatus.Used:
            raise HTTPException(status_code=400, detail="Confirmation code already used")
        
        #diff = (datetime.now() - confirmation_code.created_at).seconds
        diff = 9
        if diff > 3600 and False:
            raise HTTPException(status_code=400, detail="Confirmation code expired")
        
        #fix me later
        #edit_employee(confirmation_code.employee_id, {models.Employee.account_status: enums.AccountStatus.active})
        db_employee = db.get(models.Employee, confirmation_code.employee_id)
        db_employee.account_status = enums.AccountStatus.active
        
        # also this can
        #edit_confirmation_code(confirmation_code.id, {models.AccountActivation.status: enums.TokenStatus.Used}) 
        db_token = db.get(models.AccountActivation, confirmation_code.id)
        db_token.status = enums.TokenStatus.Used
        db.commit()

    except Exception as e: 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys))
    
    return schemas.BaseOut(
            detail="Account confirmed successfully",
            status_code=status.HTTP_200_OK,
        )


@app.post("/forgetPassword", response_model=schemas.BaseOut)
async def forget_password(entry : schemas.ForgetPassword, db: DbDep):
    employee = get_employee_by_email(db, entry.email)
    if not employee:
        return schemas.BaseOut(
            detail = "No account associated with this email",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    try:
        reset_code = add_reset_code(db, employee)
        db.flush()
        await simple_send([employee.email], {
                'name': employee.first_name,
                'code': reset_code.token,
                'psw': employee.password
            }, EmailTemplate.ResetPassword
        )
        db.commit()
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=get_error_message(text, error_keys))
    
    return schemas.BaseOut(
        detail="email has been sent",
        status_code=status.HTTP_200_OK,
    )



@app.patch("/resetPassword", response_model=schemas.BaseOut)
def reset_password(entry : schemas.ResetPassword, db: DbDep):
    try:
        reset_code = get_reset_code(db, entry.reset_code)

        if not reset_code:
            raise HTTPException(status_code=404, detail="Token not found")
        
        if reset_code.status == enums.TokenStatus.Used:
            raise HTTPException(status_code=400, detail="Token already used")
        
        diff = (datetime.now() - reset_code.created_at).seconds
        if diff > 3500:
            raise HTTPException(status_code=400, detail="Token expired")
        
        if entry.psw != entry.confirm_psw:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        db_employee = db.get(models.Employee, reset_code.employee_id)
        db_employee.password = get_password_hash(entry.psw)

        db_token = db.get(models.ResetPassword, reset_code.id)
        db_token.status = enums.TokenStatus.Used
        
        db.commit()

    except Exception as e: 
        db.rollback()
        text = str(e)
        add_error(text, db)
        raise HTTPException(status_code=500, detail=text)
    
    return schemas.BaseOut(
            detail="Password reset successfully",
            status_code=status.HTTP_200_OK,
        )