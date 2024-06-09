from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
from database.models import (
    Languages,
    InterestAreas,
    MemberProfileCurr, MemberProfileHist,
    AliasHist,
)
from schemas import s_auth, s_choices

from typing import List

from utilities.constants import (
    AddType
)

from fastapi import HTTPException
from starlette import status

async def get_used_alias(
    db: AsyncSession, 
    name: str
) -> AliasHist | None:  
    query = select(AliasHist).filter(
            (AliasHist.alias == name)
        )
    
    alias = (await db.execute(query)).scalar()

    return alias

async def create_alias_history(
    name: str
) -> AliasHist:
    new_alias = AliasHist(
        alias = name,
        add_at = func.now()
    )

    return new_alias

async def create_mem_profile_history(
    user: MemberProfileCurr
) -> MemberProfileHist:
    new_profile = MemberProfileHist(
        member_id = user.id,
        apple_id = user.apple_id,
        google_id = user.google_id,
        apple_email = user.apple_email,
        google_email = user.google_email,
        join_at = user.join_at,
        alias = user.alias,
        alias_std = user.alias_std,
        bio = user.bio,
        image = user.image,
        gender = user.gender,
        is_dating = user.is_dating,
        add_at = func.now(),
        add_type = AddType.Update
    )

    return new_profile


async def get_searched_users(
    db: AsyncSession,
    name: str,
    limit: int,
    offset: int
):

    query = (
        select(MemberProfileCurr.alias, MemberProfileCurr.id, MemberProfileCurr.image, MemberProfileCurr.bio)
        .where(MemberProfileCurr.alias.like(f"%{name}%"))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    users = results.fetchall()

    return users