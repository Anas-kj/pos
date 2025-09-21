from fastapi import FastAPI
import uvicorn

from backend.app.OAuth2 import get_curr_employee

from .external_services import email_service

from .database import get_session
from .routers import employee
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(employee.router)


#fix me:  set specific origins later
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    yield from get_session()

@app.get("/")
async def root():
    return await email_service.simple_send(["tisoha2149@litepax.com"], {
        "first_name" : "Fred",
        "last_name" : "Flintstone",
    })

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)