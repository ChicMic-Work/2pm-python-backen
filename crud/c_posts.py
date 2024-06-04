from sqlalchemy import select, asc, delete
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List

from utilities.constants import (
    AddType, ChoicesType
)

from fastapi import HTTPException
from starlette import status

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostBlogDraftRequest,
    PostBlogRequest,
    # PostCreateRequest,
    PostPollRequest,
    PostQuesDraftRequest,
    PostQuesRequest
)

from utilities.constants import (
    PostType
)

from database.models import (
    DailyAns, MemberProfileCurr, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist
)
from uuid_extensions import uuid7

#BLOG
async def create_blog_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostBlogRequest
):
    del_query = None
    if draft_id:
        del_query = delete(PostDraft).where(PostDraft.id == draft_id)

    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        title = post_request.title,
        body = post_request.body,
        interest_id = post_request.interest_area_id,
        lang_id = post_request.language_id
    )

    post_curr   = PostStatusCurr(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous
    )

    post_hist   = PostStatusHist(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous,
        add_type = AddType.Insert
    )
    
    # for tag in post_request.tags:
    #     post.tag1.append(
    #         models.PostTag(
    #             post_id = post.id,
    #             tag = tag
    #         )
    #     )
    
    return del_query, post, post_curr, post_hist

async def create_draft_blog_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostBlogDraftRequest
):
    if draft_id:

        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.title = post_request.title
        post_draft.body = post_request.body
        post_draft.interest_id = post_request.interest_area_id
        post_draft.lang_id = post_request.language_id

    else:
        
        post_draft  = PostDraft(
            member_id = member_id,
            title = post_request.title,
            body = post_request.body,
            type = post_request.type,
            interest_id = post_request.interest_area_id,
            lang_id = post_request.language_id,
            assc_post_id = None
        )
    
    return post_draft


#QUESTION
async def create_ques_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostQuesRequest
):
    
    del_query = None
    if draft_id:
        del_query = delete(PostDraft).where(PostDraft.id == draft_id)

    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        title = post_request.title,
        body = post_request.body,
        interest_id = post_request.interest_area_id,
        lang_id = post_request.language_id
    )

    post_curr   = PostStatusCurr(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous
    )

    post_hist   = PostStatusHist(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous,
        add_type = AddType.Insert
    )
    
    # for tag in post_request.tags:
    #     post.tag1.append(
    #         models.PostTag(
    #             post_id = post.id,
    #             tag = tag
    #         )
    #     )
    
    return del_query, post, post_curr, post_hist

async def create_draft_ques_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostQuesDraftRequest
):
    if draft_id:

        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.title = post_request.title
        post_draft.body = post_request.body
        post_draft.interest_id = post_request.interest_area_id
        post_draft.lang_id = post_request.language_id

    else:
        
        post_draft  = PostDraft(
            member_id = member_id,
            title = post_request.title,
            body = post_request.body,
            type = post_request.type,
            interest_id = post_request.interest_area_id,
            lang_id = post_request.language_id,
            assc_post_id = None
        )
    
    return post_draft


#ANSWER
async def create_ans_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostAnsRequest ,
):
    del_query = None
    if draft_id:
        del_query = delete(PostDraft).where(PostDraft.id == draft_id)

    if not post_request.is_for_daily:
        post    = Post(
            id = uuid7(),
            member_id = member_id,
            type = post_request.type,
            title = post_request.title,
            body = post_request.body,
            assc_post_id = post_request.post_ques_id
        )

        post_curr   = PostStatusCurr(
            post_id = post.id,
            is_anonymous = post_request.is_anonymous
        )

        post_hist   = PostStatusHist(
            post_id = post.id,
            is_anonymous = post_request.is_anonymous,
            add_type = AddType.Insert
        )
    else:
        post    = DailyAns(
            ques_id = post_request.post_ques_id,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            answer = post_request.body,
        )

        post_curr = None
        post_hist = None

    return del_query, post, post_curr, post_hist

async def create_draft_ans_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostAnsDraftRequest
):
    if draft_id:

        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.body = post_request.body

    else:
        
        post_draft  = PostDraft(
            member_id = member_id,
            title = post_request.title,
            body = post_request.body,
            type = post_request.type,
            assc_post_id = post_request.post_ques_id,
            is_for_daily = post_request.is_for_daily
        )
    
    return post_draft


#POLL
async def create_poll_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostPollRequest
):

    del_queries = []
    if draft_id:
        del_queries.append(delete(PostDraft).where(PostDraft.id == draft_id))
        del_queries.append(delete(PollQues).where(PollQues.post_id == draft_id))

    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        interest_id = post_request.interest_area_id,
        language_id = post_request.language_id,
        title = post_request.title,
        body = post_request.body
    )

    post_curr   = PostStatusCurr(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous
    )

    post_hist   = PostStatusHist(
        post_id = post.id,
        is_anonymous = post_request.is_anonymous,
        add_type = AddType.Insert
    )

    ques_list = []

    for ques in post_request.poll:
        for i in range(0, ques.choices):
            ques_list.append(
                PollQues(
                    post_id = post.id,
                    qstn_seq_num = ques.qstn_seq_num,
                    ques_text = ques.ques_text,
                    allow_multiple = ques.allow_multiple,
                    ans_seq_letter = ques.choices[i].ans_seq_letter,
                    ans_text = ques.choices[i].ans_text
                )
            )
        
    return del_queries, post, post_curr, post_hist, ques_list


async def create_draft_poll_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostPollRequest
):

    del_query = None
    if draft_id:
        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.body = post_request.body
        post_draft.title = post_request.title

        del_query = delete(PollQues).where(PollQues.post_id == post_draft.id)

    else:
        post_draft  = PostDraft(
            id = uuid7(),
            member_id = member_id,
            type = post_request.type,
            interest_id = post_request.interest_area_id,
            language_id = post_request.language_id,
            title = post_request.title,
            body = post_request.body
        )

    ques_list = []

    for ques in post_request.poll:

        for i in range(0, ques.choices):
            ques_list.append(
                PollQues(
                    post_id = post_draft.id,
                    qstn_seq_num = ques.qstn_seq_num,
                    ques_text = ques.ques_text,
                    allow_multiple = ques.allow_multiple,
                    ans_seq_letter = ques.choices[i].ans_seq_letter,
                    ans_text = ques.choices[i].ans_text
                )
            )
        
    return del_query, post_draft, ques_list









"""
async def create_post_crud(
    db: AsyncSession,
    member_id: UUID,
    post_request: PostCreateRequest
):
    if post_request.type == PostType.B:
        return Post(
            id = uuid7,
            member_id = member_id,
            intrst_id = post_request.interest_area_id,
            lang_id   = post_request.language_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
            body = post_request.body
        )
    elif post_request.type == PostType.Q:
        return Post(
            id = uuid7,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
            body = post_request.body
        )
    elif post_request.type == PostType.A:
        return Post(
            id = uuid7,
            member_id = member_id,
            ass_post_id = post_request.ass_post_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            body = post_request.body
        )
    elif post_request.type == PostType.P:
        Post(
            id = uuid7,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
        )
"""