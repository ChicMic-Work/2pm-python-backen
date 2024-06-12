import random
import string
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response

from pydantic import ValidationError

from starlette import status
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from schemas.s_auth import (
    Token, RefreshToken,
    MemberSignup, MemberSignupResponse,
    MemberProfileAuthResponse
)

from schemas.s_choices import (
    LangIAResponse
)

from redis.asyncio import Redis

from database.models import (
    MemberProfileCurr,
    SessionCurr,
    SessionPrev
)

from dependencies import (
    create_registration_token,
    get_db, 
    bcrypt_context, 
    create_access_token, 
    get_current_user
    )

from crud.c_auth import (
    create_registration_user,
    delete_session,
    get_registration_user,
    get_user_by_social_id, 
    create_user,
    create_signin_session,
    verify_apple_token,
    verify_google_token,
    get_user_by_id
    )

from crud.c_choices import (
    get_mem_choices,
    get_mem_languages,
    get_mem_interest_areas
)

from utilities.constants import (
    USER_LOGGED_OUT,
    RedisKeys,
    ResponseKeys,
    access_token_expire,
    SocialType, AuthTokenHeaderKey,
    REDIS_DB
)

"""
/auth router
Authentication
Sign-up
Login
Generate Access and Refresh Tokens
"""
router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)



"""
Generate Auth Token Based on:
email and password

@router.post(
    "/token",
    response_model = RefreshToken
    )
async def login_for_access_token(
    request: Request,
    credentials: MemberProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, credentials.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not registered")
    if not bcrypt_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Credentials")
    
    access_token, refresh_token = await create_access_token(user.email, user.id, access_token_expire)
    
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get(
    "/token/refresh",
    response_model = Token
    )
async def refresh_access_token(
    request: Request,
    auth_token:Annotated[str, Header()],
    db: AsyncSession = Depends(get_db)
):
    try:
        user_cred = get_current_user(auth_token)
        user = await authenticate_user(db, user_cred["email"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid refresh token'
            )
            
        # Generate a new access token
        access_token, _ = await create_access_token(user_cred["email"], user_cred["id"], access_token_expire)
        return {'access_token': access_token, 'token_type': 'bearer'}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token'
        )

    # create_user_request.password = bcrypt_context.hash(create_user_request.password)
"""

@router.post(
    "/login/", 
    response_model = MemberSignupResponse,
    status_code = status.HTTP_200_OK
    )
async def login_user(
    request: Request,
    create_user_request: MemberSignup,
    db: AsyncSession = Depends(get_db)
):  
    async with db.begin():
        try:
            db_user = await get_user_by_social_id(
                db, 
                create_user_request.social_id, 
                create_user_request.social_type
            )
            registration_user = False
            if not db_user:
                db_user = await get_registration_user(
                    db, 
                    create_user_request.social_id, 
                    create_user_request.social_type
                )
                registration_user = True

            ip = None
            new_user = False
            if request.client.host:
                ip = request.client.host
                
            # if create_user_request.social_type == SocialType.Apple:
            #     await verify_apple_token(create_user_request.token, create_user_request.social_id)
            # else:
            #     await verify_google_token(create_user_request.token)
            
            if db_user:
                if not db_user.alias:
                    new_user = True
                    db_user.update_at = func.now()
            else:
                db_user = await create_registration_user(db, create_user_request)
                new_user = True

            db.add(db_user)

            if not registration_user:
                session = await create_signin_session(db_user.id, ip, create_user_request)
                db.add(session)
                session_id = session.id

                access_token = await create_access_token(db_user.id, session_id, access_token_expire)
            else:
                N = 10
                session_id  = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
                
                access_token = await create_registration_token(
                    db_user.id,
                    session_id,
                    access_token_expire,
                    create_user_request.device_type,
                    create_user_request.device_model,
                    create_user_request.social_id,
                    create_user_request.social_type
                )
            
            memb_resp = None
            
            if not new_user:

                if not db_user.image:
                    image = None
                else:
                    image = db_user.image

                lang_list = []
                int_list = []

                lang_list, int_list = await get_mem_choices(db, db_user.id)

                
                if registration_user:
                    join_at = None
                else:
                    join_at = db_user.join_at

                memb_resp = MemberProfileAuthResponse(
                    alias = db_user.alias,
                    bio= db_user.bio,
                    google_id= db_user.google_id,
                    apple_id= db_user.apple_id,
                    apple_email = db_user.apple_email,
                    google_email = db_user.google_email,
                    join_at = join_at,
                    gender= db_user.gender,
                    is_dating= db_user.is_dating,
                    image= image,
                    language_choices= lang_list,
                    interest_area_choices= int_list
                )

            return MemberSignupResponse(
                token= access_token,
                new_user= new_user,
                profile= memb_resp
            )

        except Exception as exc:

            status_code = 500
            msg = str(exc)

            await db.rollback()
            raise HTTPException(status_code=status_code, detail=msg) from exc
    

@router.post(
    "/logout/",
    status_code = status.HTTP_200_OK
    )
async def user_logged_out(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):

    async with db.begin():
        try:
            red = await Redis(db = REDIS_DB)
            revoked_tokens = await red.get(RedisKeys.revoked_tokens)
            
            if revoked_tokens:
                revoked_tokens = revoked_tokens.decode('utf-8')
                revoked_tokens += f' {Auth_token}'
            else:
                revoked_tokens = Auth_token
            
            
            await red.set(RedisKeys.revoked_tokens, revoked_tokens)
            await red.close()
            
            user: MemberProfileCurr = request.user

            del_query, ses_prev = await delete_session(db, user.__getattribute__('ses'))
            await  db.execute(del_query)
            db.add(ses_prev)

            return {
                ResponseKeys.MESSAGE: USER_LOGGED_OUT
            }
        
        except Exception as exc:

            status_code = 500

            await db.rollback()
            response.status_code = status_code
            return {
                ResponseKeys.MESSAGE: str(exc)
            }
            
            
# @router.post(
#     "/logout/",
# )
# as