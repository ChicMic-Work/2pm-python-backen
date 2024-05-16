from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr
from database.models import (
    MemberProfile,
    SignInSession
)
from schemas.s_auth import (
    MemberSignup
)

import requests

from uuid import UUID
from utilities.constants import (
    current_time, SocialType,
    APPLE_TOKEN_ISS, APPLE_TOKEN_AUD,
    APPLE_AUTH_KEY_URL,GOOGLE_AUTH_KEY_URL,
    GOOGLE_TOKEN_AUD
)

from uuid_extensions import uuid7

import jwt

from fastapi import HTTPException, status

async def create_user(
    db: AsyncSession, 
    user: MemberSignup
):  

    db_user = MemberProfile(
            id = uuid7(),
            created_at= current_time,
            updated_at= current_time,
        )
    
    if user.social_type == 1:
        db_user.apple_id = user.social_id
    else:
        db_user.google_id = user.social_id

    return db_user


async def get_user_by_social_id(
    db: AsyncSession, 
    social_id: str,
    social_type: int
) -> MemberProfile | None:  
    if social_type == SocialType.Google:
        query = select(MemberProfile).filter(
            (MemberProfile.google_id == social_id)
        )
    else:
        query = select(MemberProfile).filter(
            (MemberProfile.apple_id == social_id)
        )
    
    return (await db.execute(query)).scalar()
 

async def get_user_by_id(
    db: AsyncSession,
    user_id: str
) -> MemberProfile | None:
    query = select(MemberProfile).options(
        joinedload(MemberProfile.language_choices),
        joinedload(MemberProfile.interest_area_choices)
    ).filter(MemberProfile.id == user_id)
    
    result = await db.execute(query)
    return result.scalars().first()  

"""
return (await db.scalars(select(MemberProfile).filter(MemberProfile.id == user_id))).first()
"""

async def create_signin_session(
    user_id: UUID,
    ip: str,
    create_user_request: MemberSignup
) -> SignInSession:
    session = SignInSession(
        member_id = user_id,
        signin_id = create_user_request.social_id,
        type = create_user_request.social_type,
        ip = ip,
        device_type = create_user_request.device_type,
        device_model = create_user_request.device_model
    )
    
    return session


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