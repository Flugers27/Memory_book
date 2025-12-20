# services/Auth/utils.py
from passlib.context import CryptContext
from .config import config
import smtplib
from email.message import EmailMessage

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=config.BCRYPT_ROUNDS,
    argon2__memory_cost=102400,
    argon2__parallelism=8
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def send_verification_email(email: str, token: str):
    verification_link = f"http://localhost:8000/auth/verify?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Подтвердите email по ссылке: {verification_link}")
    msg["Subject"] = "Подтверждение Email"
    msg["From"] = "flugers27@gmail.com"
    msg["To"] = email

    # Подключение к SMTP Gmail
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
    server.quit()
    print(f"Отправлено письмо на {email} с токеном: {token}")
