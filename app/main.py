from fastapi import FastAPI

from app.database import Base, engine
from app.models import User
from app.routers.auth import router as auth_router


app = FastAPI(title="FastAPI Login System")

app.include_router(auth_router)
@app.get("/")
def root():
    return {"message": "API is running"}