from sqlalchemy import select, asc, delete, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from utilities.constants import (
    AddType, ChoicesType, PostType
)

from database.models import (
    DailyAns, MemberProfileCurr, PollMemResult, PollMemReveal, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist
)
from uuid_extensions import uuid7

from crud.c_posts import (
    get_poll_post_items
)

## DRAFTS ##
#BLOG
async def get_blog_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    blogs = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Blog).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return blogs


#QUES
async def get_ques_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    questions = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Question).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return questions


#ANS
async def get_ans_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    answers = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Answer).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return answers


#POLL
async def get_poll_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    polls = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Poll).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    for poll in polls:
        poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == poll.id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
        poll.body = poll_ques.ques_text
    
    return polls



## ANSWER A QUESTION ##

async def get_post_questions_list(
    db: AsyncSession,
    limit: int,
    offset: int
) -> List[Tuple[Post, PostStatusCurr, str, str]]:
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.type == PostType.Question,
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    questions = results.fetchall()
    
    return questions


"""
async def get_post_questions(db: AsyncSession, limit: int = 10, offset: int = 0) -> List[Dict]:
    # First query to get posts and their status
    query = (
        select(Post, PostStatusCurr)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .where(
            Post.type == 'Question',
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    posts_and_statuses = results.fetchall()
    
    post_ids = [post.id for post, status in posts_and_statuses if not status.is_anonymous]

    # Conditionally fetch member details
    if post_ids:
        member_query = (
            select(Post.id, MemberProfileCurr.image, MemberProfileCurr.alias)
            .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
            .where(Post.id.in_(post_ids))
        )
        member_results = await db.execute(member_query)
        member_details = {result[0]: {"image": result[1], "alias": result[2]} for result in member_results.fetchall()}
    else:
        member_details = {}

    return [
        {
            "post": post,
            "status": {
                "is_anonymous": status.is_anonymous,
                "is_deleted": status.is_deleted,
                "is_blocked": status.is_blocked,
                "update_at": status.update_at
            },
            "member": member_details.get(post.id, {"image": None, "alias": None}) if not status.is_anonymous else {"image": None, "alias": None}
        }
        for post, status in posts_and_statuses
    ]
"""


async def get_post_question(
    db: AsyncSession,
    post_id: UUID,
    limit: int ,
    offset: int
) -> Tuple[Post, List[Tuple[Post, PostStatusCurr, str, str]]]:
    
    query = (
        select(Post, PostStatusCurr)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .where(Post.id == post_id)
    )
    results = await db.execute(query)
    post = results.fetchone()
    
    if not post:
        raise Exception("Post not found")
    if post[1].is_deleted:
        raise Exception("Post is deleted") 
    if post[1].is_blocked:
        raise Exception("Post is blocked")
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.assc_post_id == post_id
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    answers = results.fetchall()
    
    return post, answers



## TAKE A POLL ##
async def get_post_polls_list(
    db: AsyncSession,
    limit: int,
    offset: int
):
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.type == PostType.Poll,
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    
    results = await db.execute(query)
    
    polls = results.fetchall()
    
    for poll in polls:
        poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == poll[0].id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
        poll[0].body = poll_ques.ques_text
    
    return polls


async def get_post_poll(
    db: AsyncSession,
    post_id: UUID
):
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.id == post_id
        )
        .order_by(desc(Post.post_at))
    )
    
    results = await db.execute(query)
    post = results.fetchone()
    
    if not post:
        raise Exception("Post not found")
    if post[1].is_deleted:
        raise Exception("Post is deleted") 
    if post[1].is_blocked:
        raise Exception("Post is blocked")
    
    poll_items = await get_poll_post_items(db, post[0].id)
    
    return post, poll_items

async def get_member_poll_taken(
    db: AsyncSession,
    member_id: UUID,
    post_id: UUID
):
    
    query = (
        select(PollMemResult)
        .where(
            PollMemResult.member_id == member_id,
            PollMemResult.post_id == post_id
        )
    )
    results = await db.execute(query)
    
    poll_selected = results.fetchall()
    
    if not poll_selected:
        
        query = (
            select(PollMemReveal)
            .where(
                PollMemReveal.member_id == member_id,
                PollMemReveal.post_id == post_id
            )
        )
        results = await db.execute(query)
        poll_reveal = results.fetchone()
        if poll_reveal:
            return poll_reveal[0].reveal_at
        return None
    
    return poll_selected