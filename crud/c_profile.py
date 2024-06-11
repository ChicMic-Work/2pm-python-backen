from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
from crud.c_posts_list import get_post_tags_list
from database.models import (
    Languages,
    InterestAreas,
    MemberProfileCurr, MemberProfileHist,
    AliasHist,
    PollQues,
    Post,
    PostStatusCurr,
)
from schemas import s_auth, s_choices

from typing import List

from schemas.s_posts import PostAnsResponse, PostBlogQuesResponse
from utilities.constants import (
    AddType,
    PostType
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
        .where(MemberProfileCurr.alias.ilike(f"%{name}%"))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    users = results.fetchall()

    return users


async def get_user_profile_details_by_id(
    db: AsyncSession,
    user_id: UUID
):

    query = (
        select(MemberProfileCurr)
        .where(MemberProfileCurr.id == user_id)
    )

    results = await db.execute(query)
    user = results.scalar()
    
    if not user:
        raise Exception("User not found")

    return user


async def get_user_posts_details_by_user_id(
    db: AsyncSession,
    user_id: UUID,
    post_type: str,
    limit: int,
    offset: int
):

    query = (
        select(Post)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .where(
            Post.member_id == user_id, 
            Post.type == post_type,
            PostStatusCurr.is_deleted == False,
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_anonymous == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    posts = results.fetchall()
    
    return posts