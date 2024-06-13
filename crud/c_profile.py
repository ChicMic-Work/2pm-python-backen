from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
from crud.c_posts_list import get_post_tags_list
from database.models import (
    Languages, MmbFollowCurr,
    InterestAreas,
    MemberProfileCurr, MemberProfileHist,
    AliasHist, MmbFollowHist,
    PollQues,
    Post,
    PostStatusCurr,
)
from schemas import s_auth, s_choices

from typing import List

from schemas.s_posts import PostAnsResponse, PostBlogQuesResponse
from utilities.constants import (
    USER_NOT_FOUND,
    AddType,
    MemFollowType,
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


#SEARCH

async def get_follow_counts_search(
    db: AsyncSession,
    user_id: UUID,
    searching_user_id: UUID,
    check_is_following: bool = True
):
    
    followers_query = select(func.count(MmbFollowCurr.id)).where(MmbFollowCurr.followed_id == user_id)
    followers_result = await db.execute(followers_query)
    followers_count = followers_result.scalar()
    if not followers_count:
        followers_count = 0

    
    following_query = select(func.count(MmbFollowCurr.id)).where(MmbFollowCurr.following_id == user_id)
    following_result = await db.execute(following_query)
    following_count = following_result.scalar()
    if not following_count:
        following_count = 0

    result_data = {
        "followers_count": followers_count,
        "following_count": following_count
    } 
    
    if not check_is_following:
        result_data["is_following"] = True
        result_data["my_profile"] = False
        return result_data
    
    if searching_user_id == user_id:
        result_data["is_following"] = False
        result_data["my_profile"] = True
        return result_data
    
    # Query to check if searching_user_id is following user_id
    is_following_query = select(MmbFollowCurr.id).where(
        and_(
            MmbFollowCurr.following_id == searching_user_id,
            MmbFollowCurr.followed_id == user_id
        )
    )
    is_following_result = await db.execute(is_following_query)
    
    if is_following_result.scalar():
        is_following = True
    else:
        is_following = False
    
    result_data["is_following"] = is_following
    result_data["my_profile"] = False
    
    return result_data

async def get_searched_users(
    db: AsyncSession,
    name: str,
    limit: int,
    offset: int,
    searching_user_id: UUID
):
    query = (
        select(
            MemberProfileCurr.alias, 
            MemberProfileCurr.id, 
            MemberProfileCurr.image, 
            MemberProfileCurr.bio
        )
        .where(MemberProfileCurr.alias.ilike(f"%{name}%"))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    users = results.fetchall()

    # Fetch follower and following counts for each user, and if the searching user is following them
    user_data = []
    for user in users:
        follow_counts = await get_follow_counts_search(db, user[1], searching_user_id)
        user_data.append({
            "alias": user[0],
            "id": user[1],
            "image": user[2],
            "bio": user[3],
            "followers_count": follow_counts["followers_count"],
            "following_count": follow_counts["following_count"],
            "is_following": follow_counts["is_following"],
            "my_profile": follow_counts["my_profile"]
        })

    return user_data


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
        raise Exception(USER_NOT_FOUND)

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


async def get_member_followers_following(
    db: AsyncSession,
    user_id: UUID,
    limit: int,
    offset: int,
    type: str = MemFollowType.Followers
):
    if type == MemFollowType.Followers:
        query = (
            select(
                MemberProfileCurr.alias, 
                MemberProfileCurr.id, 
                MemberProfileCurr.image, 
                MemberProfileCurr.bio
            )
            .join(MemberProfileCurr, MemberProfileCurr.id == MmbFollowCurr.following_id)
            .where(MmbFollowCurr.followed_id == user_id)
            .order_by(desc(MmbFollowCurr.follow_at))
            .limit(limit)
            .offset(offset)
        )
        check_following = True
    elif type == MemFollowType.Following:
        query = (
            select(
                MemberProfileCurr.alias, 
                MemberProfileCurr.id, 
                MemberProfileCurr.image, 
                MemberProfileCurr.bio
            )
            .join(MemberProfileCurr, MemberProfileCurr.id == MmbFollowCurr.followed_id)
            .where(MmbFollowCurr.following_id == user_id)
            .order_by(desc(MmbFollowCurr.follow_at))
            .limit(limit)
            .offset(offset)
        )
        check_following = False
    else:
        raise Exception("Invalid type")

    results = await db.execute(query)
    users = results.fetchall()
    
    user_data = []
    for user in users:
        follow_counts = await get_follow_counts_search(db, user[1], user_id, check_following)
        
        user_data.append({
            "alias": user[0],
            "id": user[1],
            "image": user[2],
            "bio": user[3],
            "followers_count": follow_counts["followers_count"],
            "following_count": follow_counts["following_count"],
            "is_following": follow_counts["is_following"],
            "my_profile": follow_counts["my_profile"]
        })
        
    return user_data

