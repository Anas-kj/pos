from typing import List

from fastapi import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

from ..config import settings



conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail_username,
    MAIL_PASSWORD = settings.mail_password,
    MAIL_FROM = settings.mail_from,
    MAIL_SERVER = settings.mail_server,
    MAIL_PORT = settings.mail_port,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True, 
    TEMPLATE_FOLDER = Path(__file__).parent / "templates",
)

async def simple_send(email: list[EmailStr], body: dict ) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})   