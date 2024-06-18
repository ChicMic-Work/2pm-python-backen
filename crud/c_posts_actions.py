from sqlalchemy import exists, or_, select, asc, delete, desc, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from crud.c_profile import get_follow_counts_search
from utilities.constants import (
    INVALID_POLL_ITEM, INVALID_POST_TYPE, POLL_ALREADY_REVEALED, POLL_ALREADY_TAKEN, POST_BLOCKED, POST_DELETED, AddType, ChoicesType, PostInviteListType, PostType
)

from database.models import (
    DailyAns, MemberProfileCurr, MmbFollowCurr, PollInvite, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist, QuesInvite
)
from uuid_extensions import uuid7

#CHECK POST CURRENT STATUS
async def check_post_curr_details(
    db: AsyncSession,
    post_id: UUID
):
    
    query = (
        select(PostStatusCurr)
        .where(
            PostStatusCurr.post_id == post_id
        )
    )
    
    results = await db.execute(query)
    post_curr = results.fetchone()
    
    if post_curr[0].is_deleted:
        raise Exception(POST_DELETED) 
    if post_curr[0].is_blocked:
        raise Exception(POST_BLOCKED)
    
    return post_curr

#TAKE POLL
async def check_if_poll_items_exist(
    db: AsyncSession,
    post_id: UUID,
    poll_item_ids: List[UUID]
):
    query = (
        select(PollQues)
        .where(
            and_(
                PollQues.post_id == post_id,
                PollQues.poll_item_id.in_(poll_item_ids)
            )
        )
    )
    
    results = await db.execute(query)
    poll_items = results.scalars().all()
    
    if len(poll_items) != len(poll_item_ids):
        raise Exception(INVALID_POLL_ITEM)

    return poll_items

async def check_if_user_took_poll(
    db: AsyncSession,
    user_id: UUID,
    post_id: UUID,
    raise_exc: bool = True
):
    query = (
        select(PollMemTake)
        .where(
            PollMemTake.member_id == user_id,
            PollMemTake.post_id == post_id
        )
    )

    results = await db.execute(query)
    mem_take = results.fetchone()

    if mem_take and raise_exc:
        raise Exception(POLL_ALREADY_TAKEN)
    
    if mem_take and not raise_exc:
        return mem_take, "take"
    
    query = (
        select(PollMemReveal)
        .where(
            PollMemReveal.post_id == post_id,
            PollMemReveal.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_reveal = results.fetchone()

    if mem_reveal and raise_exc:
        raise Exception(POLL_ALREADY_REVEALED)
    
    if mem_reveal and not raise_exc:
        return mem_reveal, "reveal"
    

async def member_create_poll_entries(
    db: AsyncSession,
    post_id: UUID,
    user_id: UUID,
    poll_items: List[PollQues]
):
    # Check if the selected items are valid according to the allow_multiple flag
    questions = {}
    for item in poll_items:
        if item.qstn_seq_num not in questions:
            questions[item.qstn_seq_num] = []
        questions[item.qstn_seq_num].append(item)
    
    for seq_num, items in questions.items():
        allow_multiple = items[0].allow_multiple
        if not allow_multiple and len(items) > 1:
            raise Exception(f"Multiple choices are not allowed for question {seq_num}")

    new_entries = [
        PollMemResult(
            poll_item_id=poll_item.poll_item_id,
            post_id=post_id,
            member_id=user_id
        )
        for poll_item in poll_items
    ]
    
    poll_take = PollMemTake(
        post_id=post_id,
        member_id=user_id
    )
    
    return new_entries, poll_take
    
    
async def check_member_reveal_took_poll(
    db: AsyncSession,
    post_id: UUID,
    user_id: UUID
):
    
    query = (
        select(PollMemReveal)
        .where(
            PollMemReveal.post_id == post_id,
            PollMemReveal.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_reveal = results.fetchone()

    if mem_reveal:
        raise Exception(POLL_ALREADY_REVEALED)
    
    query = (
        select(PollMemTake)
        .where(
            PollMemTake.post_id == post_id,
            PollMemTake.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_take = results.fetchone()
    if mem_take:
        raise Exception(POLL_ALREADY_TAKEN)
    
    reveal = PollMemReveal(
        post_id=post_id,
        member_id=user_id
    )
    
    return reveal



#INVITE
async def invite_member_to_post(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    inviting_user_id: UUID
):
    if post.type == PostType.Question:
        
        _invited = QuesInvite(
            ques_post_id=post.id,
            inviting_mbr_id=inviting_user_id,
            invited_mbr_id= user_id
        )
        
    elif post.type == PostType.Poll:
        
        _invited = PollInvite(
            poll_post_id=post.id,
            inviting_mbr_id=inviting_user_id,
            invited_mbr_id= user_id
        )
        
    else:
        raise Exception(INVALID_POST_TYPE)
    
    return _invited



async def invite_member_to_post_list(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    limit: int,
    offset: int,
    type: str = PostInviteListType.FOLLOWERS,
    search: str = ""
):

    if post.type == PostType.Question:
            
        invited_subquery = (
            select(QuesInvite.invited_mbr_id)
            .where(QuesInvite.ques_post_id == post.id)
            .subquery()
        )
        
        answered_subquery = (
            select(Post.member_id)
            .where(Post.assc_post_id == post.id)
            .subquery()
        )
        
        filters = [
            MemberProfileCurr.id.notin_(answered_subquery)
        ]
            
    else: 
        
        invited_subquery = (
            select(PollInvite.invited_mbr_id)
            .where(PollInvite.poll_post_id == post.id)
            .subquery()
        )
        
        poll_taken_subquery = (
            select(PollMemTake.member_id)
            .where(
                PollMemTake.post_id == post.id,               
            )
            .subquery()
        )
        
        poll_reveal_subquery = (
            select(PollMemReveal.member_id)
            .where(
                PollMemReveal.post_id == post.id,               
            )
            .subquery()
        )
        
        filters = [
            MemberProfileCurr.id.notin_(poll_taken_subquery),
            MemberProfileCurr.id.notin_(poll_reveal_subquery)
        ]

    base_query = (
        select(
            MemberProfileCurr.alias,
            MemberProfileCurr.id,
            MemberProfileCurr.image,
            MemberProfileCurr.bio,
            exists(invited_subquery.c.invited_mbr_id)
                .where(invited_subquery.c.invited_mbr_id == MemberProfileCurr.id)
                .label("invited_already"),
            MmbFollowCurr.follow_at
        )
    )
    
    if search:
        
        combined_query = base_query.join(
            MmbFollowCurr, 
                or_(
                    MemberProfileCurr.id == MmbFollowCurr.following_id,
                    MemberProfileCurr.id == MmbFollowCurr.followed_id
                )
            ).where(
                or_(
                    MmbFollowCurr.following_id == user_id,
                    MmbFollowCurr.followed_id == user_id
                )
            )
        
        search_filter = MemberProfileCurr.alias.ilike(f"%{search}%")
        combined_query = combined_query.where(search_filter)

        for filter in filters:
            combined_query = combined_query.where(filter)

        query = combined_query.order_by(desc(MmbFollowCurr.follow_at)).limit(limit).offset(offset)
        
        check_following = True
        
    else:
        if type == PostInviteListType.FOLLOWERS:
            query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.following_id).where(
                MmbFollowCurr.followed_id == user_id
            )
            
            check_following = True
                
        elif type == PostInviteListType.FOLLOWING:
            query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.followed_id).where(
                MmbFollowCurr.following_id == user_id
            )
            
            check_following = False
        
        else:
            raise Exception("INVALID_INVITE_LIST_TYPE")

        for filter in filters:
            query = query.where(filter)

        query = query.order_by(desc(MmbFollowCurr.follow_at)).limit(limit).offset(offset)
    
    
    res = await db.execute(query)
    users = res.fetchall()
    
    users_data = []
    
    for user in users:
        
        follow_counts = await get_follow_counts_search(db, user[1], user_id, check_following)
        
        users_data.append({
            "id": user[1],
            "alias": user[0],
            "image": user[2],
            "bio": user[3],
            "invited_already": user[-2],
            "followers_count": follow_counts["followers_count"],
            "following_count": follow_counts["following_count"],
            "is_following": follow_counts["is_following"],
        })
    
    return users_data