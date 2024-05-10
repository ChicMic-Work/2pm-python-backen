from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
from database.models import (
    Languages,
    InterestAreas,
    MemberProfile,
    MemberStatus
)
from schemas import s_auth, s_choices

from typing import List

from utilities.constants import (
    current_time
)

from fastapi import HTTPException
from starlette import status

async def create_user_language_choices(
    db: AsyncSession,
    _languages: List[UUID]
) -> List[Languages]:
    languages = []
    for language_id in _languages:
        language = await db.get(Languages, language_id)
        if language:
            languages.append(language)
            
    return languages


async def create_user_interest_choices(
    db: AsyncSession,
    _interest: List[UUID]
) -> List[InterestAreas]:
    interests = []
    for interest_id in _interest:
        interest = await db.get(InterestAreas, interest_id)
        if interest:
            interests.append(interest)
            
    return interests

async def initial_member_status(
    db: AsyncSession, 
    user_id: UUID
) -> MemberStatus:
    status = MemberStatus(member_id = user_id)
    return status