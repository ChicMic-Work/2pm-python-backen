from sqlalchemy import select, asc, delete, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List

from utilities.constants import (
    AddType, ChoicesType, PostType
)

from database.models import (
    DailyAns, MemberProfileCurr, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist
)
from uuid_extensions import uuid7
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