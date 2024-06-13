from datetime import datetime
from typing import Optional
from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from sqlalchemy import select
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import (
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, create_draft_blog_post_crud, create_draft_poll_post_crud, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items
)
from crud.c_posts_actions import check_if_user_took_poll
from crud.c_posts_list import convert_all_post_list_for_response, get_cd_answers, get_hop_posts, get_mp_posts, get_ans_drafts, get_blog_drafts, get_member_dict_for_post_detail, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, get_post_question, get_post_questions_list, get_post_tags_list, get_ques_drafts, get_random_post_questions_polls_list, get_random_posts, get_searched_posts, get_searched_question_poll_list, get_user_drafted_posts
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_list import  PostQuestionResponse, QuesAnsListResponse
from utilities.constants import (
    DRAFT_NOT_FOUND, EMPTY_SEARCH_STRING, INVALID_POST_TYPE, INVALID_SEARCH_QUERY, AuthTokenHeaderKey, HOPSortType, PostListType, PostType, RandomSample, ResponseKeys, ResponseMsg
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
    DailyQues, MemberProfileCurr, PollMemResult, Post,
    PostDraft
)

from app.posts import router

@router.get(
    "/get/drafts/"
)
async def get_member_drafts(
    post_type: str,
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:

        user: MemberProfileCurr = request.user
        if post_type not in PostType.types_list:
            raise Exception(INVALID_POST_TYPE)
        
        drafts = await get_user_drafted_posts(db, user.id, post_type)

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: drafts
        }

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
@router.get(
    "/get/drafts/{draft_id}"
)
async def get_member_draft(
    draft_id: str,
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:

        user: MemberProfileCurr = request.user
        
        post_draft = await db.get(PostDraft, draft_id)
        if not post_draft:
            raise Exception(DRAFT_NOT_FOUND)
        if post_draft.member_id != user.id:
            raise Exception(DRAFT_NOT_FOUND)
        
        member = {"alias": user.alias}
        
        if post_draft.type == PostType.Blog or post_draft.type == PostType.Question:
            
            post_draft = PostBlogQuesResponse(
                post_id = str(post_draft.id),
                member= member,
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                post_at= post_draft.save_at,
            )
            
        elif post_draft.type == PostType.Answer:
            post_draft = PostAnsResponse(
                post_id = str(post_draft.id),
                member= member,
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,

                post_ques_id= post_draft.assc_post_id,
                is_for_daily= post_draft.is_for_daily,
                
                post_at= post_draft.save_at
            )
            
        elif post_draft.type == PostType.Poll:
            post_draft = PostPollResponse(
                post_id = str(post_draft.id),
                member= member,
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                post_at= post_draft.save_at,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                poll= await get_poll_post_items(db, post_draft.id)
            )
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: post_draft
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        

@router.get(
    "/get/questions/"
)
async def get_member_questions(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    type: str = PostListType.random,
    search: Optional[str] = None
):
    try:
        
        user: MemberProfileCurr = request.user
        
        if type == PostListType.random:
            questions = await get_random_post_questions_polls_list(db, user.id, limit, RandomSample._5, RandomSample._5, PostType.Question)
        elif type == PostListType.search:
            if not search:
                raise Exception(INVALID_SEARCH_QUERY)
            questions = await get_searched_question_poll_list(db, user.id, search ,limit, offset, PostType.Question)
        else:
            questions = await get_post_questions_list(db, user.id, limit, offset)
        
        
        res_data = []
        
        for ques in questions:
            tags = get_post_tags_list(ques[0])
            
            member = get_member_dict_for_post_detail(ques[1], image=ques[2], alias= ques[3])
            
            res_data.append(PostBlogQuesResponse(
                post_id = str(ques[0].id),
                member= member,
                
                title= ques[0].title,
                body= ques[0].body,
                type= ques[0].type,
                
                interest_area_id= ques[0].interest_id,
                language_id= ques[0].lang_id,
                
                post_at= ques[0].post_at,
                tags= tags
            ))
        
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
        
@router.get(
    "/get/questions/{post_id}"
)
async def get_member_question(
    request: Request,
    response: Response,
    post_id: str,
    limit: int = 10,
    offset: int = 0,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:

        user: MemberProfileCurr = request.user
        
        post, answers = await get_post_question(db, post_id, limit, offset)
        
        ans_list = []
        
        for ans in answers:
            member = get_member_dict_for_post_detail(ans[1], image=ans[2], alias= ans[3])
            
            ans_list.append(QuesAnsListResponse(
                post_id = str(ans[0].id),
                member= member,
                type= ans[0].type,
                title= ans[0].title,
                body= ans[0].body,
                post_at= ans[0].post_at 
            ))
        
        tags = get_post_tags_list(post[0])
        member = get_member_dict_for_post_detail(post[1], image=post[2], alias= post[3])
        
        post = PostBlogQuesResponse(
            post_id = str(post[0].id),
            member= member,
            
            type= post[0].type,
            title= post[0].title,
            body= post[0].body,
            tags=tags,
            interest_area_id= post[0].interest_id,
            language_id= post[0].lang_id,
            post_at= post[0].post_at
        )
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: {"ans_list": ans_list, "post": post}
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
        
@router.get(
    "/get/polls/"
)
async def get_member_polls(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    type: str = PostListType.random,
    search: Optional[str] = None
):
    try:

        user: MemberProfileCurr = request.user
        
        if type == PostListType.random:
            polls = await get_random_post_questions_polls_list(db, user.id, limit, 5, 5, PostType.Poll)
        elif type == PostListType.search:
            if not search:
                raise Exception(INVALID_SEARCH_QUERY)
            polls = await get_searched_question_poll_list(db, user.id, search, limit, offset, PostType.Poll)
        else:
            polls = await get_post_polls_list(db, user.id, limit, offset)
        
        res_data = []
        
        for ques in polls:
            tags = get_post_tags_list(ques[0])
            
            member = get_member_dict_for_post_detail(ques[1], image=ques[2], alias= ques[3])
            
            res_data.append(PostBlogQuesResponse(
                post_id = str(ques[0].id),
                member= member,
                
                title= ques[0].title,
                body= ques[0].body,
                type= ques[0].type,
                
                interest_area_id= ques[0].interest_id,
                language_id= ques[0].lang_id,
                
                post_at= ques[0].post_at,
                tags= tags
            ))
        
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
        

@router.get(
    "/get/polls/{post_id}"
)
async def get_member_poll(
    request: Request,
    response: Response,
    post_id: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:

        user: MemberProfileCurr = request.user

        try:
            await check_if_user_took_poll(db, user.id, post_id)
            post, poll_items = await get_post_poll(db, post_id)
        except:
            post, poll_items = await get_post_poll(db, post_id, True)

        member = get_member_dict_for_post_detail(post[1], image=post[2], alias= post[3])
        
        tags = get_post_tags_list(post[0])

        
        poll_data = PostPollResponse(
            post_id = str(post[0].id),
            member= member,
            
            type= post[0].type,
            title= post[0].title,
            body= post[0].body,
            
            tags= tags,
            interest_area_id= post[0].interest_id,
            language_id= post[0].lang_id,
            
            post_at= post[0].post_at,
            poll= poll_items
        )
        
        
        poll_reveal = None
        mem_poll = []
        mem_poll_status = await get_member_poll_taken(db, user.id, post_id)
        
        if mem_poll_status:
            if isinstance(mem_poll_status[0], datetime):
                poll_reveal = mem_poll_status[0]
            elif isinstance(mem_poll_status, list):
                for poll in mem_poll_status:
                    mem_poll.append(
                        str(poll[0].poll_item_id)
                    )
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: {
                "poll": poll_data,
                "reveal_at": poll_reveal,
                "selected_choices": mem_poll,
            }
        }
                    
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
        
@router.get(
    "/hop/"
)
async def hot_off_press(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    sort_type: str = HOPSortType.newest
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_hop_posts(db, limit, offset, sort_type)

        res_posts = await convert_all_post_list_for_response(db, posts)

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_posts
        }
                

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
    

@router.get(
    "/cd/"
)
async def club_daily_answers(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_cd_answers(db, limit, offset)
        res_posts = []

        for post in posts:
            
            member = get_member_dict_for_post_detail(post[0], image=post[2], alias= post[3])

            res_posts.append(PostAnsResponse(
                post_id = str(post[0].id),
                member= member,
                
                type= PostType.Answer,
                
                title= post[1],
                body= post[0].answer,
                
                post_ques_id=str(post[0].ques_id),
                is_for_daily= True,
                
                post_at= post[0].post_at
            ))

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_posts
        }
    
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
    

@router.get(
    "/mp/"
)
async def most_popular_posts(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    interest: int = None
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_mp_posts(db, limit, offset, interest)

        res_posts = []
        
        if posts:
            res_posts = await convert_all_post_list_for_response(db, posts, n=1)

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_posts
        }
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }


@router.get(
    "/search/"
)
async def search_posts(
    request: Request,
    response: Response,
    search: str,
    limit: int = 10,
    offset: int = 0,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user
        
        if not search.strip():
            raise Exception(EMPTY_SEARCH_STRING)
        
        posts = await get_searched_posts(db, search.strip(), limit, offset)

        res_posts = []
        if posts:
            res_posts = await convert_all_post_list_for_response(db, posts)

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_posts
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        

@router.get(
    "/pr/"
)
async def pure_random_posts(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_random_posts(db, 70, 5, limit)

        res_posts = []
        if posts:
            res_posts = await convert_all_post_list_for_response(db, posts)

        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: res_posts
        }

        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }