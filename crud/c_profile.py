from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
from database.models import (
    Languages,
    InterestAreas,
    MemberProfile,
    MemberStatus,
    AliasHist,
    MemAliasHist
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


async def create_initial_member_status(
    db: AsyncSession, 
    user_id: UUID
) -> MemberStatus:
    status = MemberStatus(member_id = user_id)
    return status


async def get_used_alias(
    db: AsyncSession, 
    name: str
) -> AliasHist | None:  
    query = select(AliasHist).filter(
            (AliasHist.alias == name)
        )

    return (await db.execute(query)).scalar()


async def create_user_alias(
    name: str,
    normalized_alias: str,
    user_id: UUID
) -> AliasHist | None:  
    
    mem_alias = MemAliasHist(
        member_id = user_id,
        alias = name
    )
    
    all_alias = AliasHist(
        alias = normalized_alias
    )

    return mem_alias, all_alias