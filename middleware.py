from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dependencies import get_current_user
from crud.c_auth import get_registration_user_by_id, get_user_by_id
from dependencies import get_db
from database.models import SessionLocal

from utilities.constants import AuthTokenHeaderKey, protected_endpoints, REDIS_DB

"""
# Middleware function to check JWT token for selected endpoints
async def jwt_token_middleware(request: Request, call_next):
    
    # List of endpoints that require token authentication
    protected_endpoints = ['/tr']

    if request.url.path in protected_endpoints:
        # Get the authorization header
        try:
            authorization: HTTPAuthorizationCredentials = HTTPBearer().convert(request)
        except Exception as e:
            print(e)

        payload = get_current_user(request.headers[AuthTokenHeaderKey])
        request.user = payload

        response = await call_next(request)
        return response

    # Continue to the endpoint for unprotected routes
    response = await call_next(request)
    return response

{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWQiOiIwMThmNTZmMS0zNTcwLTc5ZTYtODA5YS1lOGUxYzVjMWUxNTgiLCJleHAiOjE3MTUxODYwODB9.NQ-ybdyIbLtjqMjhL4GaADkB77dA-azjPi40pQG-WE0",
    "token_type": "bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWQiOiIwMThmNTZmMS0zNTcwLTc5ZTYtODA5YS1lOGUxYzVjMWUxNTgiLCJleHAiOjE3MTc3NzgwODB9.JHpPKydcCVKdQU9EFwriAI-fKdr9HSOWh1U1R9jkNMw"
}
"""



from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser, UnauthenticatedUser
)

from starlette.middleware.authentication import AuthenticationMiddleware

from redis.asyncio import Redis

class RequestUser(BaseUser):
    def __init__(self, user) -> None:
        self.user = user
        self.email = user.email

    @property
    def is_authenticated(self) -> bool:
        return True
    
    @property
    def is_active(self) -> bool:
        return self.is_active

    @property
    def display_name(self) -> str:
        return self.email
    
    @property
    def identity(self) -> str:
        return str(self.user.id)


class BearerTokenAuthBackend(AuthenticationBackend):
    
    async def authenticate(self, request: Request):

        for endpoint in protected_endpoints:
            if request.url.path.startswith(endpoint):
                
                
                if AuthTokenHeaderKey not in request.headers:
                    raise AuthenticationError('Provide authorization credentials')

                auth_token = request.headers[AuthTokenHeaderKey]
                token = auth_token #.split(' ')[1]
                
                red = await Redis(db = REDIS_DB)
                revoked_tokens = await red.get('revoked_tokens')
                if revoked_tokens:
                    revoked_tokens = revoked_tokens.decode('utf-8')
                    if auth_token in revoked_tokens:
                        raise AuthenticationError('Unauthorized Access')
                await red.close()

                user_cred = get_current_user(token, True)
                
                async with SessionLocal() as db:
                    reg_user = False
                    if user_cred["reg_user"]:
                        user = await get_registration_user_by_id(db, user_cred["id"])
                        reg_user = True
                    else:
                        user = await get_user_by_id(db, user_cred["id"])

                if not user:
                    raise AuthenticationError('Unauthorized Access')
                user.__setattr__('ses', user_cred["ses"])

                user.__setattr__('reg_user', reg_user)
                    

                return AuthCredentials(["authenticated"]), user
        
        return  AuthCredentials(["anonymous"]), UnauthenticatedUser()