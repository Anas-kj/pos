from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session
import uvicorn
from . import schemas
from .database import create_db_and_tables, get_session
from app.routers import employee as crud

async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Dependency
def get_db():
    yield from get_session()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)