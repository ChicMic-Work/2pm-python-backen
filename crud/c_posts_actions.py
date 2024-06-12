from sqlalchemy import select, asc, delete, desc, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from utilities.constants import (
    INVALID_POLL_ITEM, POLL_ALREADY_REVEALED, POLL_ALREADY_TAKEN, POST_BLOCKED, POST_DELETED, AddType, ChoicesType, PostType
)

from database.models import (
    DailyAns, MemberProfileCurr, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist
)
from uuid_extensions import uuid7


#check if poll items exist and are of same post
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

async def check_poll_details_before_take(
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


async def check_if_user_took_poll(
    db: AsyncSession,
    user_id: UUID,
    post_id: UUID
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

    if mem_take:
        raise Exception(POLL_ALREADY_TAKEN)
    
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