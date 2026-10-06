from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI(
    title="DeliveryAPI - FastAPI"
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ouath2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

from routes import auth, pedidos

app.include_router(auth.router)
app.include_router(pedidos.router)