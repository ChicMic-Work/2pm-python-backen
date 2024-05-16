from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, Request

from pydantic import ValidationError

from starlette import status
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.s_auth import (
    Token, RefreshToken,
    MemberSignup, MemberSignupResponse,
    MemberProfileAuthResponse
)

from dependencies import (
    get_db, 
    bcrypt_context, 
    create_access_token, 
    get_current_user
    )

from crud.c_auth import (
    get_user_by_social_id, 
    create_user,
    create_signin_session,
    verify_apple_token,
    verify_google_token,
    get_user_by_id
    )

from crud.c_profile import (
    create_initial_member_status
)

from utilities.constants import (
    access_token_expire,
    SocialType
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
    try:
        db_user = await get_user_by_social_id(
            db, 
            create_user_request.social_id, 
            create_user_request.social_type
        )
        
        ip = None
        new_user = False
        if request.client.host:
            ip = request.client.host
            
        # if create_user_request.social_type == SocialType.Apple:
        #     await verify_apple_token(create_user_request.token, create_user_request.social_id)
        # else:
        #     await verify_google_token(create_user_request.token)
        
        if db_user:
            session = await create_signin_session(db_user.id, ip, create_user_request)
            if not db_user.alias:
                new_user = True
            db.add(session)
        else:
            db_user = await create_user(db, create_user_request)
            # mem_status = await create_initial_member_status(db, db_user.id)
            session = await create_signin_session(db_user.id, ip, create_user_request)
            new_user = True
            db.add(db_user)
            # db.add(mem_status)
            db.add(session)
            
        await db.commit()
        await db.refresh(db_user)
            
        access_token = await create_access_token(db_user.id, access_token_expire)
        
        memb_resp = None
        if not new_user:
            db_user = await get_user_by_id(db, db_user.id)
            memb_resp = MemberProfileAuthResponse(
                alias = db_user.alias,
                bio= db_user.bio,
                gender= db_user.gender,
                is_dating= db_user.is_dating,
                image= db_user.image,
                language_choices= db_user.language_choices,
                interest_area_choices= db_user.interest_area_choices
            )

        return MemberSignupResponse(
            token= access_token,
            new_user= new_user,
            profile= memb_resp
        )

    except Exception as exc:
        if hasattr(exc, "detail") and hasattr(exc, "status_code"):
            msg = exc.detail
            status_code = exc.status_code
        else:
            status_code = 500
            msg = str(exc)

        await db.rollback()
        raise HTTPException(status_code=status_code, detail=msg) from exc
    
