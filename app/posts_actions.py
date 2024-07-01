from datetime import datetime
from uuid import UUID
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
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, create_draft_blog_post_crud, 
    create_draft_poll_post_crud, create_poll_post_crud, create_ques_post_crud, create_draft_ques_post_crud, 
    get_poll_post_items
)
from crud.c_posts_actions import (
    check_existing_report, check_if_poll_items_exist, check_if_user_took_poll, 
    check_member_reveal_took_poll, check_post_curr_details, invite_mem_post_list, invite_member_to_post, 
    invite_member_to_post_list, member_comment_like_unlike, member_create_poll_entries, member_follow_ques_poll, member_like_daily_ans, member_like_post, 
    member_mark_fav_post, member_report_content, recommend_member_to_post_list
)
from crud.c_posts_list import (
    get_ans_drafts, get_blog_drafts, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, 
    get_post_question, get_post_questions_list, get_ques_drafts
)
from crud.c_profile import get_member_followers_following
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_actions import MemTakePollReq, ReportReasonReq
from schemas.s_posts_list import PostQuestionResponse, QuesAnsListResponse
from utilities.constants import (
    ALREADY_INVITED, CANT_FOLLOW_POST, CANT_INVITE_TO_POST, CANT_INVITE_YOURSELF, 
    CANT_REPORT_SELF, COMMENT_NOT_FOUND, DUPLICATE_POLL_ITEM_IDS, FOLLOWED, INVALID_REPORT_TYPE, 
    LIKED, POLL_ITEM_NOT_FOUND, POST_NOT_FOUND, UNFOLLOWED, UNLIKE, USER_NOT_FOUND, AuthTokenHeaderKey,
    PostInviteListType, PostType, ReportType, ResponseKeys, ResponseMsg
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
    CommentNode, DailyAns, DailyAnsLike, DailyCommentNode, DailyQues, MemberProfileCurr, PollMemResult, PollQues, Post,
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
    "/invite/user/list/"
)
async def list_for_inviting_members(
    request: Request,
    response: Response,
    post_id: str,
    limit: int = 10,
    offset: int = 0,
    type: str = PostInviteListType.FOLLOWING,
    search: str = "",
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
        
        if type != PostInviteListType.RECOMMENDATION:
            res_data = await invite_member_to_post_list(db, post, user.id, limit, offset, type, search.strip())
        else:
            res_data = await recommend_member_to_post_list(db, post, user.id, limit, offset)
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_data
        }
        
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
    post_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):

    try:
        
        user: MemberProfileCurr = request.user
        
        invited_user = await db.get(MemberProfileCurr, user_id)
        if not invited_user:
            raise Exception(USER_NOT_FOUND)
        if invited_user.id == user.id:
            raise Exception(CANT_INVITE_YOURSELF)        
        
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
        

@router.get(
    "/invite/list/{post_id}"
)
async def list_received_sent_invites(
    request: Request,
    response: Response,
    post_id: str,
    limit: int = 10,
    offset: int = 0,
    type: str = PostInviteListType.RECEIVED,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        await check_post_curr_details(db, post.id)
        
        res_data = await invite_mem_post_list(db, post, user.id, limit, offset, type)
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_data
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }


@router.post(
    "/follow/{post_id}"
)
async def follow_post(
    request: Request,
    response: Response,
    post_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        if post.type not in (PostType.Question, PostType.Poll):
            raise Exception(CANT_FOLLOW_POST)
        
        await check_post_curr_details(db, post.id)
        
        del_query, hist, curr = await member_follow_ques_poll(db, post, user.id)
        
        if del_query:
            await db.delete(del_query)
            msg = UNFOLLOWED
        else:
            db.add(curr)
            msg = FOLLOWED
            
        db.add(hist)
        
        return {
            ResponseKeys.MESSAGE: msg
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        

@router.post(
    "/fav/{post_id}"
)
async def fav_post(
    request: Request,
    response: Response,
    post_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        post = await db.get(Post, post_id)
        if not post:
            raise Exception(POST_NOT_FOUND)
        
        await check_post_curr_details(db, post.id)
        
        del_query, hist, curr = await member_mark_fav_post(db, post, user.id)
        
        if del_query:
            await db.delete(del_query)
            msg = UNFOLLOWED
        else:
            db.add(curr)
            msg = FOLLOWED
            
        db.add(hist)
        
        return {
            ResponseKeys.MESSAGE: msg
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
        
@router.post(
    "/like/{post_id}"
)
async def like_post(
    request: Request,
    response: Response,
    post_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            post = await db.get(Post, post_id)
            if not post:
                
                daily_ans = await db.get(DailyAns, post_id)
                
                if not daily_ans:
                    raise Exception(POST_NOT_FOUND)
            
            if post:
                await check_post_curr_details(db, post.id)
                
                del_query, hist, curr = await member_like_post(db, post, user.id)
                
                if del_query:
                    await db.delete(del_query)
                    msg = UNLIKE
                    
                else:
                    db.add(curr)
                    msg = LIKED
                    
                db.add(hist)
            
            else:
                
                liked = await member_like_daily_ans(db, user.id, daily_ans)
                
                if liked:
                    msg = UNLIKE
                    await db.delete(daily_ans)
                else:
                    db.add(
                        DailyAnsLike(
                            member_id = user.id,
                            daily_answer_id = daily_ans.id
                        )
                    )
                    msg = LIKED
                
            
            return {
                ResponseKeys.MESSAGE: msg
            }
            
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc),
                ResponseKeys.DATA: None
            }
        
        
@router.post(
    "/report/{content_id}"
)
async def report_post(
    request: Request,
    response: Response,
    content_id: str,
    reason: ReportReasonReq,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user
        
        if reason.content_type == ReportType.MESSAGE:
            await check_existing_report(db, user.id, content_id, True)
        else:
            await check_existing_report(db, user.id, content_id, False)
        
        if reason.content_type not in ReportType._list:
            raise Exception(INVALID_REPORT_TYPE)
        
        if reason.content_type == ReportType.POST:
            post = await db.get(Post, content_id)
            if not post:
                raise Exception(POST_NOT_FOUND)
            if post.member_id == user.id:
                raise Exception(CANT_REPORT_SELF)
            await check_post_curr_details(db, post.id)
        
        if reason.content_type == ReportType.HOMEPAGE:
            if user.id == UUID(content_id):
                raise Exception(CANT_REPORT_SELF)
            
        if reason.content_type == ReportType.COMMENT:
            
            n_cmnt = await db.get(CommentNode, content_id)
            
            if not n_cmnt:
                d_cmnt = await db.get(DailyCommentNode, content_id)
                if not d_cmnt:
                    raise Exception(COMMENT_NOT_FOUND)
                if d_cmnt.member_id == user.id:
                    raise Exception(CANT_REPORT_SELF)
            
            if n_cmnt.member_id == user.id:
                raise Exception(CANT_REPORT_SELF)
                
        report = await member_report_content(db, user.id, content_id, reason)
        
        db.add(report)
        await db.commit()
        
        return {
            ResponseKeys.MESSAGE: "Reported"
        }

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        

@router.post(
    "/comment/like/{comment_id}"
)
async def like_comment(
    request: Request,
    response: Response,
    comment_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfileCurr = request.user

        comment = await db.get(CommentNode, comment_id)
        daily = False

        if not comment:
            comment = await db.get(DailyCommentNode, comment_id)
            daily = True
            if not comment:
                raise Exception(COMMENT_NOT_FOUND)
            
        _liked, check = await member_comment_like_unlike(db, user.id, comment, daily)

        if check:
            msg = UNLIKE
            db.delete(_liked)
        else:
            msg = LIKED
            db.add(_liked)

        await db.commit()

        return {
            ResponseKeys.MESSAGE: msg
        }

    except Exception as exc:
        await db.rollback()
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
    


