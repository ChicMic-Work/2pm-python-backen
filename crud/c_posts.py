from sqlalchemy import exists, func, select, asc, delete, update
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from math import (floor)

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Union

from crud.c_choices import check_interest_choices, check_language_choices
from utilities.common import normalize_tag
from utilities.constants import (
    AddType, ChoicesType
)

from fastapi import HTTPException
from starlette import status

from schemas.s_posts import (
    PollQuesChoicesDraftRequest,
    PollQuesChoicesRequest,
    PollQuestionDraftReq,
    PollQuestionRequest,
    PostAnsDraftRequest,
    PostAnsRequest,
    PostBlogDraftRequest,
    PostBlogRequest,
    PostPollDraftRequest,
    # PostCreateRequest,
    PostPollRequest,
    PostQuesDraftRequest,
    PostQuesRequest
)

from utilities.constants import (
    PostType, current_datetime
)

from database.models import (
    DailyAns, DailyQues, MemberProfileCurr, PollMemResult, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist, QuesInvite, TagList
)
from uuid_extensions import uuid7


async def create_forum_tag(
    db: AsyncSession,
    tag: str
):
    
    _ex = normalize_tag(tag)
    
    query = select(TagList).where(
        
    )
    
    query = (
        select(exists().where(
            TagList.name == _ex
        ))
    )
    
    if not (await db.execute(query)).scalar():
        return TagList(
            name = tag,
            add_date = current_datetime().date()
        )


def add_post_tags(post: Post, tags: List[str]):
    try:
        if tags[0]:
            post.tag1 = tags[0]
        if tags[1]:
            post.tag2 = tags[1]
        if tags[2]:
            post.tag3 = tags[2]
    except:pass
    

async def check_choices_for_posts(
    db: AsyncSession,
    language_id: int,
    interest_id: int
):
    await check_language_choices(db, [language_id], True)
    await check_interest_choices(db, [interest_id], True)


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

    await check_choices_for_posts(db, post_request.language_id, post_request.interest_area_id)
    
    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        title = post_request.title,
        body = post_request.body,
        interest_id = post_request.interest_area_id,
        lang_id = post_request.language_id,
        post_at= current_datetime()
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
    add_post_tags(post, post_request.tags)
    
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
        post_draft.save_at = current_datetime()

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
    await check_choices_for_posts(db, post_request.language_id, post_request.interest_area_id)
    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        title = post_request.title,
        body = post_request.body,
        interest_id = post_request.interest_area_id,
        lang_id = post_request.language_id,
        post_at= current_datetime()
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
    
    add_post_tags(post, post_request.tags)
    
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
        post_draft.save_at = current_datetime()

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
    ques: Union[Post, DailyQues]
):
    del_query = None
    if draft_id:
        del_query = delete(PostDraft).where(PostDraft.id == draft_id)

    if not post_request.is_for_daily:
        post    = Post(
            id = uuid7(),
            member_id = member_id,
            type = post_request.type,
            title = " ",
            body = post_request.body,
            assc_post_id = post_request.post_ques_id,
            post_at= current_datetime()
        )
        
        add_post_tags(post, [" ", None, None])
        

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
            id = uuid7(),
            ques_id = post_request.post_ques_id,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            answer = post_request.body,
            post_at= current_datetime()
        )

        post_curr = None
        post_hist = None

    return del_query, post, post_curr, post_hist

async def create_draft_ans_post_crud(
    db: AsyncSession,
    member_id: UUID,
    draft_id: UUID,
    post_request: PostAnsDraftRequest,
    ques: Union[Post, DailyQues]
):
    if draft_id:

        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.body = post_request.body
        post_draft.save_at = current_datetime()

    else:
        
        post_draft  = PostDraft(
            member_id = member_id,
            body = post_request.body,
            title= ques.title,
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
        
    await check_choices_for_posts(db, post_request.language_id, post_request.interest_area_id)

    post    = Post(
        id = uuid7(),
        member_id = member_id,
        type = post_request.type,
        interest_id = post_request.interest_area_id,
        lang_id = post_request.language_id,
        title = post_request.title,
        body = post_request.body,
        post_at= current_datetime()
    )
    
    add_post_tags(post, post_request.tags)

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
        for i in range(0, len(ques.choices)):
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
    post_request: PostPollDraftRequest
):

    del_query = None
    if draft_id:
        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception("Draft not found")
        post_draft.body = post_request.body
        post_draft.title = post_request.title
        post_draft.save_at = current_datetime()

        del_query = delete(PollQues).where(PollQues.post_id == post_draft.id)

    else:
        post_draft  = PostDraft(
            id = uuid7(),
            member_id = member_id,
            type = post_request.type,
            interest_id = post_request.interest_area_id,
            lang_id = post_request.language_id,
            title = post_request.title,
            body = post_request.body
        )

    ques_list = []

    for ques in post_request.poll:

        for i in range(0, len(ques.choices)):
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

async def get_poll_post_items(
    db: AsyncSession,
    post_id: UUID,
    get_percentage: bool = False,
    is_draft: bool = False
):

    result = await db.execute(select(PollQues).where(PollQues.post_id == post_id))
    poll_data = result.scalars().all()
    
    poll_dict = {}
    
    for detail in poll_data:
        qstn_key = (detail.qstn_seq_num, detail.ques_text)
        if qstn_key not in poll_dict:
            poll_dict[qstn_key] = {
                "qstn_seq_num": detail.qstn_seq_num,
                "ques_text": detail.ques_text,
                "allow_multiple": detail.allow_multiple,
                "choices": []
            }
        poll_dict[qstn_key]["choices"].append({
            "poll_item_id": str(detail.poll_item_id),
            "ans_seq_letter": detail.ans_seq_letter,
            "ans_text": detail.ans_text,
            "selected_count": None,
            "percentage": None
        })

    if get_percentage:
        
        poll_results = (await db.execute(
            select(
                PollMemResult.poll_item_id,
                PollQues.qstn_seq_num,
                func.count(PollMemResult.poll_item_id).label('vote_count')
            )
            .join(PollQues, PollMemResult.poll_item_id == PollQues.poll_item_id)
            .where(PollMemResult.post_id == post_id)
            .group_by(PollMemResult.poll_item_id, PollQues.qstn_seq_num)
        )).all()
        
        poll_item_counts = {}
        total_votes_per_question = {}
        
        for poll_item_id, qstn_seq_num, vote_count in poll_results:
            if qstn_seq_num not in total_votes_per_question:
                total_votes_per_question[qstn_seq_num] = 0
            total_votes_per_question[qstn_seq_num] += vote_count
            poll_item_counts[poll_item_id] = vote_count
        
        for qstn_key, qstn_data in poll_dict.items():
            total_votes = total_votes_per_question.get(qstn_key[0], 0)
            for choice in qstn_data["choices"]:
                poll_item_id = UUID(choice["poll_item_id"])
                choice_votes = poll_item_counts.get(poll_item_id, 0)
                if choice_votes > 0:
                    choice["selected_count"] = choice_votes
                else:
                    choice["selected_count"] = 0
                if total_votes > 0:
                    choice["percentage"] = floor((choice_votes / total_votes) * 100)
                else:
                    choice["percentage"] = 0

    if is_draft:
        poll_questions = [
                PollQuestionDraftReq(
                qstn_seq_num=k[0],
                ques_text=k[1],
                allow_multiple=v["allow_multiple"],
                choices=[PollQuesChoicesDraftRequest(**choice) for choice in v["choices"]]
            )
            for k, v in poll_dict.items()
        ]
    else:
        poll_questions = [
            PollQuestionRequest(
                qstn_seq_num=k[0],
                ques_text=k[1],
                allow_multiple=v["allow_multiple"],
                choices=[PollQuesChoicesRequest(**choice) for choice in v["choices"]]
            )
            for k, v in poll_dict.items()
        ]
    
    return poll_questions


async def add_ans_to_invited_ques(
    db: AsyncSession,
    ques: Post,
    ans: Post,
    member_id: UUID,
):

    query = (
        update(QuesInvite)
        .where(
            QuesInvite.invited_mbr_id == member_id,
            QuesInvite.ques_post_id == ques.id
        )
        .values(ans_post_id=ans.id)
    )
    
    
    return query