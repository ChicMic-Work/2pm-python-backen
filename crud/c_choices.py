from sqlalchemy import select, asc, delete, func, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
import pytz

from uuid import UUID
from uuid_extensions import uuid7
from database.models import (
    MemberLang, MemberProfileCurr,
    Languages, InterestAreas,
    MemberIA
)
from database.table_keys import InterestAreaKeys, LanguageKeys
from schemas.s_choices import(
    LangIACreate,
    LangIAResponse
) 

from typing import List

from utilities.constants import (
     ChoicesType
)

from fastapi import HTTPException
from starlette import status

async def create_language_choices(
    db: AsyncSession,
    _languages: List[LangIACreate]
) -> List[Languages]:
    languages = []
    
    for language in _languages:
        # existing_language = (await db.scalars(select(models.Languages).filter(models.Languages.name == language.name))).first()

        query = select(Languages).filter(Languages.name == language.name)
        existing_language = await db.execute(query)

        if existing_language.scalar():
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f"Language '{language.name}' already exists")
        
        new_language = Languages(
                name= language.name,
                add_date= datetime.now(pytz.utc).date()
            )
        
        languages.append(new_language)
        
    return languages

async def create_interest_choices(
    db: AsyncSession,
    _interest: List[LangIACreate]
) -> List[InterestAreas]:
    interests = []
    
    for interest in _interest:

        query = select(InterestAreas).filter(InterestAreas.name == interest.name)
        existing_interest = await db.execute(query)

        if existing_interest.scalar():
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f"Topic Area '{interest.name}' already exists")
        
        new_interest = InterestAreas(
                name= interest.name,
                add_date= datetime.now(pytz.utc).date()
            )
        
        interests.append(new_interest)
        
    return interests

async def get_all_created_choices(
    db: AsyncSession,
    type: int
) -> List[Languages] | List[InterestAreas]:
    list_choices = []
    if type not in (0,1):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= f"type :{type}, is not valid")
    if type == ChoicesType.Language:
        query = select(Languages).order_by(asc(LanguageKeys.add_date))
    elif type == ChoicesType.Interest_Area:
        query = select(InterestAreas).order_by(asc(InterestAreaKeys.add_date))
        
    result = await db.execute(query)
    return result.scalars().all()

async def check_language_choices(
    db: AsyncSession,
    _languages: List[int]
) -> List[int]:
    languages = []
    for language_id in _languages:
        language = await db.get(Languages, language_id)
        if language:
            languages.append(language_id)
            
    return languages

async def check_interest_choices(
    db: AsyncSession,
    _interest: List[int]
) -> List[int]:
    interests = []
    for interest_id in _interest:
        interest = await db.get(InterestAreas, interest_id)
        if interest:
            interests.append(interest_id)
            
    return interests

async def create_mem_languages(
    db: AsyncSession,
    mem_id: UUID,
    languages: List[int],
    del_old: bool
):
    languages = await check_language_choices(db, languages)

    if del_old:
        del_query = f"DELETE FROM mbr.mbr_language WHERE mbr_id = :mem_id"

        await db.execute(text(del_query), {'mem_id': mem_id})

    new_entries = [MemberLang(member_id=mem_id, language_id=lang_id) for lang_id in languages]
    
    return new_entries

async def create_mem_interst_areas(
    db: AsyncSession,
    mem_id: UUID,
    interests: List[int],
    del_old: bool
):
    interests = await check_interest_choices(db, interests)

    await db.execute(delete(MemberIA).where(MemberIA.member_id == mem_id))

    new_entries = [MemberIA(member_id=mem_id, int_area_id=int_id) for int_id in interests]

    return new_entries


async def get_mem_languages(
    db: AsyncSession,
    mem_id: UUID
) -> List[Languages]:

    stmt = (
            select(MemberLang.language_id, Languages.name, Languages.add_date)
            .join(Languages, MemberLang.language_id == Languages.id)
            .where(MemberLang.member_id == mem_id)
        )
    
    result = await db.execute(stmt)
    return result.fetchall()

async def get_mem_interest_areas(
    db: AsyncSession,
    mem_id: UUID
) -> List[InterestAreas]:


    stmt = (
            select(MemberIA.int_area_id, InterestAreas.name, InterestAreas.add_date)
            .join(InterestAreas, MemberIA.int_area_id == InterestAreas.id)
            .where(MemberIA.member_id == mem_id)
        )
    
    result = await db.execute(stmt)
    return result.fetchall()

async def get_mem_choices(
    db: AsyncSession,
    user_id: UUID
):
    lang_list = []
    int_list = []

    language_choices = await get_mem_languages(db, user_id)
    if language_choices:
        lang_list = []
        for i in language_choices:
            lang_list.append(LangIAResponse(
                id = i[0],
                name = i[1],
                add_date= i[2]
            ))

    interest_area_choices = await get_mem_interest_areas(db, user_id)
    if interest_area_choices:
        for i in interest_area_choices:
            int_list.append(LangIAResponse(
                id = i[0],
                name = i[1],
                add_date= i[2]
            ))

    return lang_list, int_list

"""
languages = await create_user_language_choices(db, create_user_request.language_choices)
created_user.language_choices.extend(languages)

interests = await create_user_interest_choices(db, create_user_request.interest_area_choices)
created_user.interest_area_choices.extend(interests)

created_user = await get_user_choices(db, created_user.id)
created_user = await db.get(MemberProfile, created_user.id)
"""