from datetime import timedelta, datetime
import pytz
from typing import Annotated

# fastapi
from fastapi import HTTPException
from starlette import status
from starlette.authentication import AuthenticationError

# constants
from utilities.constants import SECRET_KEY, ALGORITHM

# db
from database.models import SessionLocal

# jwt
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from uuid import UUID

bcrypt_context = CryptContext(schemes=['bcrypt'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        await db.close()
        
        
async def create_access_token(
    user_id: UUID, 
    ses_id: UUID,
    expires: timedelta
):
    try:
        expires_access = datetime.now(pytz.utc) + expires
        access_payload = {'id': str(user_id), 'exp': expires_access, 'ses': str(ses_id)} #'sub': email, 
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        pass
    # expires_refresh = expires_access + timedelta(days=30)
    # refresh_payload = {'id': str(user_id), 'exp': expires_refresh}
    # refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"""
          {access_token}
        
    """)
    #   {refresh_token}
    
    return access_token #, refresh_token


def get_current_user(token: str, middleware = False):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('id')
        if user_id is None:
            if middleware:
                raise AuthenticationError('Could not validate user')
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        return {'id': user_id, 'ses': payload.get('ses')}
    except ExpiredSignatureError:
        raise AuthenticationError('Token Expired')
    except JWTError:
        if middleware:
            raise AuthenticationError('Could not validate user')
        raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )