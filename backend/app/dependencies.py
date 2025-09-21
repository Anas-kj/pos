from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session
from fastapi import Depends

from backend.app.OAuth2 import get_curr_employee
from .main import get_db

DbDep = Annotated[Session, Depends(get_db)]

class PaginationParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokenDep = Annotated[str, Depends(oauth2_scheme)]
formDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]

def get_current_employee(db: DbDep, token: tokenDep):
    return get_curr_employee(db, token)