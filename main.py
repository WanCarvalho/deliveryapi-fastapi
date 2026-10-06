from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=30

app = FastAPI(
    title="DeliveryAPI - FastAPI"
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from routes import auth, pedidos

app.include_router(auth.router)
app.include_router(pedidos.router)