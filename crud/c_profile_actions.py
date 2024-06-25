import random
from sqlalchemy import select, asc, delete, desc, func, and_, or_, text
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from schemas.s_posts import PostAnsResponse, PostBlogQuesResponse, PostPollResponse
from utilities.constants import (
    AddType, ChoicesType, PaginationLimit, PostType, current_datetime
)

from datetime import datetime, timedelta

from database.models import (
    DailyAns, DailyQues, MemberProfileCurr, MmbFollowCurr, MmbFollowHist, MmbSpamCurr, MmbSpamHist, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist, ViewPostScore
)
from uuid_extensions import uuid7


async def follow_unfollow_user(
    db: AsyncSession,
    user_id: UUID,
    member_id: UUID
):
    _del = None
    
    _hist = MmbFollowHist(
        followed_id = member_id,
        following_id = user_id,
        add_type = AddType.Add
    )
    
    query = (
        select(MmbFollowCurr)
        .where(
            MmbFollowCurr.followed_id == member_id,
            MmbFollowCurr.following_id == user_id
        )
    )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        _del = result
        _hist.add_type = AddType.Delete 
        
    else:
        result = MmbFollowCurr(
            followed_id = member_id,
            following_id = user_id
        )
    
    return _del, _hist, result


async def spam_non_spam_user(
    db: AsyncSession,
    spam_id: UUID,
    user_id: UUID,
):
    _del = None
    
    _hist = MmbSpamHist(
        spam_mem_id = spam_id,
        member_id = user_id,
        add_type = AddType.Add
    )
    
    query = (
        select(MmbSpamCurr)
        .where(
            MmbSpamCurr.spam_mem_id == spam_id,
            MmbSpamCurr.member_id == user_id
        )
    )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        _del = result
        _hist.add_type = AddType.Delete 
        
    else:
        result = MmbSpamCurr(
            spam_mem_id = spam_id,
            member_id = user_id
        )
    
    return _del, _hist, result