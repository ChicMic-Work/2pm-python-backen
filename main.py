from fastapi import (
    Depends, FastAPI, 
    HTTPException, Header,
    Request, Security
)

from fastapi.security.api_key import APIKeyHeader

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_mail import (
    FastMail, 
    MessageSchema, 
    ConnectionConfig, 
    MessageType
)

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from middleware import BearerTokenAuthBackend

from starlette.middleware.authentication import AuthenticationMiddleware

from typing import Annotated

from app import auth, choices, profile, posts, posts_list
from utilities.constants import (
    EMAIL_HOST,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_PORT,
    DEFAULT_FROM_EMAIL,
    AuthTokenHeaderKey
)
import redis

app = FastAPI()
app.include_router(auth.router)
app.include_router(choices.router)
app.include_router(profile.router)
app.include_router(posts.router)

app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend())

templates = Jinja2Templates(directory="templates")

token_key = APIKeyHeader(name="Authorization")

conf = ConnectionConfig(
    MAIL_USERNAME = EMAIL_HOST_USER,
    MAIL_PASSWORD = EMAIL_HOST_PASSWORD,
    MAIL_FROM = EMAIL_HOST_USER,
    MAIL_PORT = EMAIL_PORT,
    MAIL_SERVER = EMAIL_HOST,
    MAIL_FROM_NAME= "Team 2PM",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


@app.get("/")
def default(
    request: Request,
    db: AsyncSession = Depends(get_db)
):  
    return '2PM Club'

@app.get("/template_check", response_class=HTMLResponse)
async def send_email_check(
    request: Request, 
    name: str, 
    username: str,
    url: str,
    email: str
):
    with open("templates/welcome.html", "r") as file:
        _html = file.read()
    
    rendered_html = _html.format(
        username= username,
        name= name,
        url= url,
        help_url= url
    )
        
    
    message = MessageSchema(
        subject="Welcome to 2PM Club",
        recipients= [email],
        body= rendered_html,
        subtype=MessageType.html)
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return templates.TemplateResponse(
        request=request, 
        name="welcome.html", 
        context={ 
            "name": name, 
            "username": username,
            "url": url,
            "help_url": url}
    )