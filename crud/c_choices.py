from sqlalchemy import select, asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
import database.models as models
from schemas import s_auth, s_choices

from typing import List

from utilities.constants import (
    current_time, ChoicesType
)

from fastapi import HTTPException
from starlette import status

async def create_language_choices(
    db: AsyncSession,
    _languages: List[s_choices.LangIACreate]
) -> List[models.Languages]:
    languages = []
    
    for language in _languages:
        # existing_language = (await db.scalars(select(models.Languages).filter(models.Languages.name == language.name))).first()

        query = select(models.Languages).filter(models.Languages.name == language.name)
        existing_language = await db.execute(query)

        if existing_language.scalar():
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f"Language '{language.name}' already exists")
        
        new_language = models.Languages(
                name= language.name,
                create_date= current_time.date()
            )
        
        languages.append(new_language)
        
    return languages

async def create_interest_choices(
    db: AsyncSession,
    _interest: List[s_choices.LangIACreate]
) -> List[models.InterestAreas]:
    interests = []
    
    for interest in _interest:

        query = select(models.InterestAreas).filter(models.InterestAreas.name == interest.name)
        existing_interest = await db.execute(query)

        if existing_interest.scalar():
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f"Language '{interest.name}' already exists")
        
        new_interest = models.InterestAreas(
                name= interest.name,
                create_date= current_time.date()
            )
        
        interests.append(new_interest)
        
    return interests

async def get_all_created_choices(
    db: AsyncSession,
    type: int
) -> List[models.Languages] | List[models.InterestAreas]:
    list_choices = []
    if type not in (0,1):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= f"type :{type}, is not valid")
    if type == ChoicesType.Language:
        query = select(models.Languages).order_by(asc(models.LanguageKeys.create_data))
    elif type == ChoicesType.Interest_Area:
        query = select(models.InterestAreas).order_by(asc(models.InterestAreaKeys.create_data))
        
    result = await db.execute(query)
    return result.scalars().all()

"""
languages = await create_user_language_choices(db, create_user_request.language_choices)
created_user.language_choices.extend(languages)

interests = await create_user_interest_choices(db, create_user_request.interest_area_choices)
created_user.interest_area_choices.extend(interests)

created_user = await get_user_choices(db, created_user.id)
created_user = await db.get(MemberProfile, created_user.id)
"""