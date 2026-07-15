from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(title="FastAPI Login System")

app.include_router(auth_router)
app.include_router(users_router)

# Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def root():
    return {"message": "API is running"}

