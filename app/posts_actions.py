from datetime import datetime
from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import (
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, create_draft_blog_post_crud, create_draft_poll_post_crud, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items
)
from crud.c_posts_actions import check_if_poll_items_exist, check_if_user_took_poll, check_member_reveal_took_poll, check_post_curr_details, invite_member_to_post, member_create_poll_entries
from crud.c_posts_list import get_ans_drafts, get_blog_drafts, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, get_post_question, get_post_questions_list, get_ques_drafts
from crud.c_profile import get_member_followers_following
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_actions import MemTakePollReq
from schemas.s_posts_list import PostQuestionResponse, QuesAnsListResponse
from utilities.constants import (
    ALREADY_INVITED, CANT_INVITE_TO_POST, DUPLICATE_POLL_ITEM_IDS, POLL_ITEM_NOT_FOUND, POST_NOT_FOUND, USER_NOT_FOUND, AuthTokenHeaderKey, PostInviteListType, PostType, ResponseKeys, ResponseMsg
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
        
        if len(choices.poll_item_ids) != len(set(choices.poll_item_ids)):
            raise Exception(DUPLICATE_POLL_ITEM_IDS)

        poll_item = await db.get(PollQues, choices.poll_item_ids[0])

        if not poll_item:
            raise Exception(POLL_ITEM_NOT_FOUND)

        post = await db.get(Post, poll_item.post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)

        post_curr = await check_post_curr_details(db, post.id)

        poll_items = await check_if_poll_items_exist(db, post.id, choices.poll_item_ids)

        #check if user already took poll or revealed poll
        await check_if_user_took_poll(db, user.id, post.id)

        #create poll member result
        new_entries, poll_take = await member_create_poll_entries(db, post.id, user.id,poll_items)
        
        poll = await get_poll_post_items(db, post.id, True)
        
        db.add_all(new_entries)
        db.add(poll_take)
        await db.commit()

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: poll
        }

    except Exception as exc:
        await db.rollback()
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        

@router.post(
    "/reveal/poll/{post_id}"
)
async def member_reveal_poll(
    request: Request,
    post_id: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        mem_reveal = await check_member_reveal_took_poll(db, user.id, post_id)
        
        poll = await get_poll_post_items(db, post.id, True)
        
        db.add(mem_reveal)
        await db.commit()
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: poll
        }
        
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: poll
        }
        


@router.get(
    "/invite/user/"
)
async def list_for_inviting_members(
    request: Request,
    response: Response,
    post_id: str = "DONT USE THIS",
    limit: int = 10,
    offset: int = 0,
    type: str = PostInviteListType.FOLLOWING,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        if post.type not in (PostType.Question, PostType.Poll):
            raise Exception(CANT_INVITE_TO_POST)
        
        await check_post_curr_details(db, post.id)
        
        users = await get_member_followers_following(db, user.id, limit, offset, type)
        
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }

@router.post(
    "/invite/user/{post_id}"
)
async def invite_member_to_a_post(
    request: Request,
    user_id: str,
    response: Response,
    post_id: str = "DONT USE THIS",
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):

    try:
        
        user: MemberProfileCurr = request.user
        
        invited_user = await db.get(MemberProfileCurr, user_id)
        if not invited_user:
            raise Exception(USER_NOT_FOUND)
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        await check_post_curr_details(db, post.id)
        
        invited = await invite_member_to_post(db, post, invited_user.id, user.id)
        
        db.add(invited)
        await db.commit()
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS
        }
    
    except IntegrityError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: ALREADY_INVITED,
            ResponseKeys.DATA: None
        }
    
    except Exception as exc:
        await db.rollback()
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
