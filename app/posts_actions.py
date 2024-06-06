from datetime import datetime
from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import (
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, create_draft_blog_post_crud, create_draft_poll_post_crud, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items
)
from crud.c_posts_actions import check_if_poll_items_exist, check_if_user_took_poll, check_poll_details_before_take, member_create_poll_entries
from crud.c_posts_list import get_ans_drafts, get_blog_drafts, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, get_post_question, get_post_questions_list, get_ques_drafts
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_actions import MemTakePollReq
from schemas.s_posts_list import PostQuestionResponse, QuesAnsListResponse
from utilities.constants import (
    AuthTokenHeaderKey, PostType
)

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostAnsResponse,
    PostBlogDraftRequest,
    PostBlogQuesResponse,
    # PostCreateRequest,
    PostBlogRequest,
    PostPollRequest,
    PostPollResponse,
    PostQuesDraftRequest,
    PostQuesRequest
)

from database.models import (
    DailyQues, MemberProfileCurr, PollMemResult, PollQues, Post,
    PostDraft
)

from app.posts import router


@router.post(
    "/take/poll/"
    )
async def member_take_poll(
    request: Request,
    choices: MemTakePollReq,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        if len(choices.poll_item_ids) != set(choices.poll_item_ids):
            raise Exception("Duplicate poll item ids")

        poll_item = await db.get(PollQues, choices.poll_item_ids[0])

        if not poll_item:
            raise Exception("Poll item not found")

        post = await db.get(Post, poll_item.post_id)
        if not post:
            raise Exception("Post not found")

        #check if post is not deleted or blocked
        post_curr = await check_poll_details_before_take(db, post.id)

        poll_items = await check_if_poll_items_exist(db, post.id, choices.poll_item_ids)

        #check if user already took poll or revealed poll
        await check_if_user_took_poll(db, user.id, post.id)

        #create poll member result
        new_entries = await member_create_poll_entries(db, user.id, post.id, choices.poll_item_ids, poll_items)

        return {
            "message": "success"
        }

    except Exception as exc:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": str(exc)
        }
        

@router.post(
    "/reveal/poll/"
    )
async def member_reveal_poll(
    request: Request,
    post_request: PostPollRequest,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
    except Exception as exc:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": str(exc)
        }