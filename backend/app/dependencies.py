from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session
from fastapi import Depends

from backend.app import models

from .OAuth2 import get_curr_employee 

from .database import get_session

DbDep = Annotated[Session, Depends(get_session)]

class PaginationParams:
    def __init__(self, page_size: int = 10, page_number: int = 1):
        self.page_size = page_size
        self.page_number = page_number

paginationParams = Annotated[PaginationParams, Depends()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokenDep = Annotated[str, Depends(oauth2_scheme)]
formDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]

def get_current_employee(db: DbDep, token: tokenDep):
    return get_curr_employee(db, token)

currentEmployee = Annotated[models.Employee, Depends(get_current_employee)]