from fastapi import FastAPI

from app.database import Base, engine
from app.models import User


app = FastAPI(title="FastAPI Login System")


@app.get("/")
def root():
    return {"message": "API is running"}