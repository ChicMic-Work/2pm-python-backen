from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr

from database.models import (
    MemberProfileCurr, MemberProfileHist,
    SessionCurr, SessionPrev
)
from schemas.s_auth import (
    MemberSignup
)

import requests

from uuid import UUID
from utilities.constants import (
    SocialType,
    APPLE_TOKEN_ISS, APPLE_TOKEN_AUD,
    APPLE_AUTH_KEY_URL,GOOGLE_AUTH_KEY_URL,
    GOOGLE_TOKEN_AUD, AddType
)

from uuid_extensions import uuid7

import jwt

from fastapi import HTTPException, status

async def create_user(
    db: AsyncSession, 
    user: MemberSignup
):  

    db_user = MemberProfileCurr(
            id = uuid7(),
            join_at= func.now(),
            update_at = func.now()
        )
    
    db_user_hist = MemberProfileHist(
        member_id = db_user.id,
        join_at= db_user.join_at,
        add_type= AddType.Insert,
        add_at= func.now()
    )

    if user.social_type == 1:

        db_user.apple_id = user.social_id
        db_user.apple_email = user.email_id

        db_user_hist.apple_id = user.social_id
        db_user_hist.apple_email = user.email_id

    else:

        db_user.google_id = user.social_id
        db_user.google_email = user.email_id

        db_user_hist.google_id = user.social_id
        db_user_hist.google_email = user.email_id



    return db_user, db_user_hist


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
 

async def get_user_by_id(
    db: AsyncSession,
    user_id: str
) -> MemberProfileCurr | None:
    query = select(MemberProfileCurr).filter(
            (MemberProfileCurr.id == user_id)
        )
    
    return (await db.execute(query)).scalar()  

"""
return (await db.scalars(select(MemberProfile).filter(MemberProfile.id == user_id))).first()
"""

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


async def delete_session(
    db: AsyncSession,
    ses_id
):
    
    del_query = delete(SessionCurr).where(SessionCurr.id == ses_id)
    curr_ses =  await db.get(SessionCurr, ses_id)
    if not curr_ses:
        raise Exception("Session does not exist")
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
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid Social Token")
        
        
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
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid Social Token")