from fastapi import FastAPI
import uvicorn

from backend.app.OAuth2 import get_curr_employee
from backend.app.routers import auth

from .database import get_session
from .routers import employee
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(employee.app)
app.include_router(auth.app)


#fix me:  set specific origins later
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    pass

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)