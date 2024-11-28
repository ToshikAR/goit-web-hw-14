import logging
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.app_users.services_auth import auth_service
from src.config.config import conf

conf = ConnectionConfig(
    MAIL_USERNAME=conf.MAIL_USERNAME,
    MAIL_PASSWORD=conf.MAIL_PASSWORD,
    MAIL_FROM=conf.MAIL_FROM,
    MAIL_PORT=conf.MAIL_PORT,
    MAIL_FROM_NAME=conf.MAIL_FROM_NAME,
    MAIL_SERVER=conf.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        logging.error(f"Send email error: {err}")


# sending email with reset password
async def send_email_pass(email: EmailStr, username: str, password: str):
    try:
        message = MessageSchema(
            subject="Reset Password",
            recipients=[email],
            template_body={"password": password, "username": username},
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="pass_email.html")
    except ConnectionErrors as err:
        logging.error(f"Send email error: {err}")
