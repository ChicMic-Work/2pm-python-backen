from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr

from database.models import (
    MemberProfileCurr, MemberProfileHist, MemberRegistration,
    SessionCurr, SessionPrev
)
from schemas.s_auth import (
    MemberSignup
)

import requests

from uuid import UUID
from utilities.constants import (
    INVALID_SOCIAL_TOKEN,
    SESSION_NOT_EXIST,
    SocialType,
    APPLE_TOKEN_ISS, APPLE_TOKEN_AUD,
    APPLE_AUTH_KEY_URL,GOOGLE_AUTH_KEY_URL,
    GOOGLE_TOKEN_AUD, AddType
)

from uuid_extensions import uuid7

import jwt

from fastapi import HTTPException, status

async def  create_registration_user(
    db: AsyncSession, 
    user: MemberSignup
):  

    db_user = MemberRegistration(
            id = uuid7(),
            update_at = func.now()
        )

    if user.social_type == SocialType.Apple:

        db_user.apple_id = user.social_id
        db_user.apple_email = user.email_id

    else:

        db_user.google_id = user.social_id
        db_user.google_email = user.email_id

    return db_user


async def create_user(
    db: AsyncSession, 
    user: MemberRegistration
):  

    db_user = MemberProfileCurr(
            id = user.id,
            join_at= func.now(),
            update_at = func.now(),
            bio = user.bio,
            is_dating = user.is_dating,
            gender = user.gender,
            alias = user.alias,
            alias_std = user.alias_std,
            image = user.image
        )
    
    db_user_hist = MemberProfileHist(
        member_id = db_user.id,
        join_at= db_user.join_at,
        add_type= AddType.Insert,
        add_at= func.now(),
        bio = user.bio,
        is_dating = user.is_dating,
        gender = user.gender,
        alias = user.alias,
        alias_std = user.alias_std,
        image = user.image
    )

    db_user.apple_id = user.apple_id
    db_user.apple_email = user.apple_email

    db_user_hist.apple_id = user.apple_id
    db_user_hist.apple_email = user.apple_email

    db_user.google_id = user.google_id
    db_user.google_email = user.google_email

    db_user_hist.google_id = user.google_id
    db_user_hist.google_email = user.google_email

    del_query = delete(MemberRegistration).where(
        MemberRegistration.id == user.id
    )

    return del_query, db_user, db_user_hist


async def get_user_by_social_id(
    db: AsyncSession, 
    social_id: str,
    social_type: int
) -> MemberProfileCurr | None:  
    if social_type == SocialType.Google:
        query = select(MemberProfileCurr).filter(
            (MemberProfileCurr.google_id == social_id)
        )
    else:
        query = select(MemberProfileCurr).filter(
            (MemberProfileCurr.apple_id == social_id)
        )
    
    return (await db.execute(query)).scalar()
 

async def get_registration_user(
    db: AsyncSession,
    social_id: str,
    social_type: int
):

    if social_type == SocialType.Google:
        query = select(MemberRegistration).filter(
            (MemberRegistration.google_id == social_id)
        )
    else:
        query = select(MemberRegistration).filter(
            (MemberRegistration.apple_id == social_id)
        )
    
    return (await db.execute(query)).scalar()


async def get_user_by_id(
    db: AsyncSession,
    user_id: str
) -> MemberProfileCurr | None:
    query = select(MemberProfileCurr).filter(
            (MemberProfileCurr.id == user_id)
        )
    
    return (await db.execute(query)).scalar()  

async def get_registration_user_by_id(
    db: AsyncSession,
    user_id: str
) -> MemberRegistration | None:
    query = select(MemberRegistration).filter(
            (MemberRegistration.id == user_id)
        )
    
    return (await db.execute(query)).scalar()


async def create_signin_session(
    user_id: UUID,
    ip: str,
    create_user_request: MemberSignup
) -> SessionCurr:
    session = SessionCurr(
        id = uuid7(),
        member_id = user_id,
        signin_id = create_user_request.social_id,
        ip = ip,
        device_type = create_user_request.device_type,
        device_model = create_user_request.device_model,
        signin_at = func.now()
    )

    if create_user_request.social_type == SocialType.Apple:
        session.type = SocialType._1
    else:
        session.type = SocialType._0
    
    return session

def create_reg_user_sign_in_session(
    user_id: UUID,
    ip: str,
    social_id: str,
    device_type: str,
    device_model: str,
    type: str
) -> SessionCurr:
    session = SessionCurr(
        id = uuid7(),
        member_id = user_id,
        signin_id = social_id,
        ip = ip,
        device_type = device_type,
        device_model = device_model,
        signin_at = func.now(),
    )
    if type == SocialType.Apple:
        session.type = SocialType._1
    else:
        session.type = SocialType._0
    
    return session

async def delete_session(
    db: AsyncSession,
    ses_id
):
    
    del_query = delete(SessionCurr).where(SessionCurr.id == ses_id)
    curr_ses =  await db.get(SessionCurr, ses_id)
    if not curr_ses:
        raise Exception(SESSION_NOT_EXIST)
    ses_prev = SessionPrev(
        id = ses_id,
        member_id = curr_ses.member_id,
        signin_id = curr_ses.signin_id,
        type = curr_ses.type,
        ip = curr_ses.ip,
        device_type = curr_ses.device_type,
        device_model = curr_ses.device_model,
        signin_at = curr_ses.signin_at,
        signout_at = func.now()
    )

    return del_query, ses_prev


async def verify_apple_token(
    token: str,
    social_id: str
):
    try:
        header = jwt.get_unverified_header(token)

        response = requests.get(APPLE_AUTH_KEY_URL)
        response.raise_for_status()
        response_json = response.json()["keys"]
        
        keys = [key['kid'] for key in response_json]
        
        if header["kid"] not in keys:
            raise
        
        payload = jwt.decode(
                token,
                "",
                verify=False,
                options={"verify_signature": False},
                algorithms=[header['alg']],
            )
        
        if payload["iss"] != APPLE_TOKEN_ISS:
            raise
        
        if payload["aud"] != APPLE_TOKEN_AUD:
            raise
        
        if payload["sub"] != social_id:
            raise
            
    except:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= INVALID_SOCIAL_TOKEN)
        
        
async def verify_google_token(
    token: str,
):
    try:
        
        params = {
            "id_token":token
        }

        response = requests.get(GOOGLE_AUTH_KEY_URL, params)
        response.raise_for_status()
        response_json = response.json()
        
        if response_json["aud"] != GOOGLE_TOKEN_AUD:
            raise
            
    except:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= INVALID_SOCIAL_TOKEN)