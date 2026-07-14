from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import Base, engine, get_db
from . import models
from .auth import hash_password,verify_password
app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="my_super_secret_key"
)

Base.metadata.create_all(bind=engine)
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@app.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing:
        return HTMLResponse(
            "<h2>Email already exists.</h2>",
            status_code=400
        )

    user = models.User(
        username=username,
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/", status_code=303)
@app.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user:
        return HTMLResponse(
            "<h2>Invalid Email or Password</h2>",
            status_code=401
        )

    if not verify_password(password, user.password):
        return HTMLResponse(
            "<h2>Invalid Email or Password</h2>",
            status_code=401
        )

    response = RedirectResponse(
    url="/home",
    status_code=303
    )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["email"] = user.email

    return response
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):

    if "user_id" not in request.session:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "username": request.session["username"]
        }
    )

@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/", status_code=303)