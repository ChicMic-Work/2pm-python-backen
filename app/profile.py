from crud.c_profile import (
    create_user_language_choices,
    create_user_interest_choices
)

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_choices import (
    LangIACreate, LangIAResponse,
    ChoicesCreate
)

from schemas.s_profile import (
    MemberProfileCreate,
    MemberProfileResponse
)

from database.models import (
    Languages, InterestAreas,
    MemberProfile
)

from utilities.constants import (
    current_time,
    AuthTokenHeaderKey
)

from typing import (
    List
)

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db


router = APIRouter(
    prefix='/profile',
    tags=['profile'],
)


@router.post(
    "/create",
    response_model = MemberProfileResponse
    )
async def create_profile(
    request: Request,
    profile: MemberProfileCreate,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfile = await get_user_by_id(db, request.user.id)
        user.alias = profile.alias
        user.bio = profile.bio
        user.gender = profile.gender
        user.image = profile.image
        
        interests = await create_user_interest_choices(db, profile.interest_area_choices)
        languages = await create_user_language_choices(db, profile.language_choices)
        
        user.language_choices.extend(languages)
        user.interest_area_choices.extend(interests)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
        
        
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail= str(exc)) from exc