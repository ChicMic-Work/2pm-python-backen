from datetime import datetime
from typing import Optional
from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from starlette import status
import os
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from crud.c_posts import (
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, create_draft_blog_post_crud, create_draft_poll_post_crud, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items
)
from crud.c_posts_actions import check_if_user_took_poll
from crud.c_posts_list import check_if_user_answered_question, club_daily_post_answers, convert_all_post_list_for_response, convert_poll_post_for_response, get_cd_ques_list, get_hop_posts, get_invited_question_poll_list, get_mp_posts, get_ans_drafts, get_blog_drafts, get_member_dict_for_post_detail, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, get_post_question, get_post_questions_list, get_post_tags_list, get_ques_drafts, get_random_post_questions_polls_list, get_random_posts, get_searched_posts, get_searched_question_poll_list, get_user_drafted_posts
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_list import  PostQuestionResponse, QuesAnsListResponse
from utilities.constants import (
    DAILY_QUES_NOT_FOUND, DRAFT_NOT_FOUND, EMPTY_SEARCH_STRING, INVALID_POST_TYPE, INVALID_SEARCH_QUERY, 
    AuthTokenHeaderKey, HOPSortType, PostListType, PostType, RandomSample, ResponseKeys, ResponseMsg,
    REDIS_DB
)

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostAnsResponse,
    PostBlogDraftRequest,
    PostBlogQuesResponse,
    # PostCreateRequest,
    PostBlogRequest,
    PostPollDraftResponse,
    PostPollRequest,
    PostPollResponse,
    PostQuesDraftRequest,
    PostQuesRequest
)

from database.models import (
    DailyQues, MemberProfileCurr, PollMemResult, Post,
    PostDraft, PostStatusCurr
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
            post_draft = PostPollDraftResponse(
                post_id = str(post_draft.id),
                member= member,
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                post_at= post_draft.save_at,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                poll= await get_poll_post_items(db, post_draft.id, is_draft= True)
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
            questions = await get_random_post_questions_polls_list(db, user.id, limit, RandomSample._50, RandomSample._10, PostType.Question)
        elif type == PostListType.search:
            if not search.strip():
                raise Exception(INVALID_SEARCH_QUERY)
            questions = await get_searched_question_poll_list(db, user.id, search.strip() ,limit, offset, PostType.Question)
        elif type == PostListType.invites:
            invited = await get_invited_question_poll_list(db, user.id, limit, offset, PostType.Question)
            
            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
                ResponseKeys.DATA: invited
            }
            
        else:
            questions = await get_post_questions_list(db, user.id, limit, offset)
        
        
        res_data = []
        
        for ques in questions:
            tags = get_post_tags_list(ques[0])
            
            member = get_member_dict_for_post_detail(ques[1], image=ques[2], alias= ques[3], user_id=ques[4])
            
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
            member = get_member_dict_for_post_detail(ans[1], image=ans[2], alias= ans[3], user_id= ans[4])
            
            ans_list.append(QuesAnsListResponse(
                post_id = str(ans[0].id),
                member= member,
                type= ans[0].type,
                title= ans[0].title,
                body= ans[0].body,
                post_at= ans[0].post_at 
            ))
        
        tags = get_post_tags_list(post[0])
        member = get_member_dict_for_post_detail(post[1], image=post[2], alias= post[3], user_id= post[4])
        
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
        
        is_answered = await check_if_user_answered_question(db, user.id, post_id)
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: {
                "ans_list": ans_list, 
                "post": post,
                "is_answered": True if is_answered == True else False
            }
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
            polls = await get_random_post_questions_polls_list(db, user.id, limit, RandomSample._50, RandomSample._10, PostType.Poll)
        elif type == PostListType.search:
            if not search.strip():
                raise Exception(INVALID_SEARCH_QUERY)
            polls = await get_searched_question_poll_list(db, user.id, search.strip(), limit, offset, PostType.Poll)
        elif type == PostListType.invites:
            invited = await get_invited_question_poll_list(db, user.id, limit, offset, PostType.Poll)
            
            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
                ResponseKeys.DATA: invited
            }
        else:
            polls = await get_post_polls_list(db, user.id, limit, offset)
        
        res_data = []
        
        for ques in polls:
            tags = get_post_tags_list(ques[0])
            
            member = get_member_dict_for_post_detail(ques[1], image=ques[2], alias= ques[3], user_id= ques[4])
            
            res_data.append(await convert_poll_post_for_response(db, ques[0], member, tags))
        
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

        member = get_member_dict_for_post_detail(post[1], image=post[2], alias= post[3], user_id= post[4])
        
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
        taken_at = None
        mem_poll = []
        
        mem_poll_status = await check_if_user_took_poll(db, user.id, post_id, False)
        
        if mem_poll_status:
            
            if mem_poll_status[1] == "take":
                taken_at = mem_poll_status[0][0].take_at
                _m_p = await get_member_poll_taken(db, user.id, post_id)
                for poll in _m_p:
                    mem_poll.append(
                        str(poll[0].poll_item_id)
                    )
            
            if mem_poll_status[1] == "reveal":
                poll_reveal = mem_poll_status[0][0].reveal_at
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            ResponseKeys.DATA: {
                "poll": poll_data,
                "reveal_at": poll_reveal,
                "selected_choices": mem_poll,
                "taken_at": taken_at
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
async def club_daily_questions_list(
    request: Request,
    response: Response,
    query_date: str,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    try:
        user: MemberProfileCurr = request.user
        
        query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        
        posts = await get_cd_ques_list(db, query_date, limit, offset)
        res_posts = []

        for post in posts:
            member = None
            post_type = PostType.Question
            ans_id = None
            if post[3]:
                ans_id = str(post[2])
                post_type = PostType.Answer
                _curr = PostStatusCurr(
                    is_anonymous= post[-1],
                )
                member = get_member_dict_for_post_detail(_curr, image=post[-3], alias= post[-4], user_id= post[-2])

            res_posts.append(PostAnsResponse(
                post_id = ans_id,
                member= member,
                
                type= post_type,
                
                title= post[1],
                body= post[3],
                
                post_ques_id=str(post[0]),
                is_for_daily= True,
                
                post_at= post[4]
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
    "/cd/{post_id}"
)
async def club_daily_answers(
    post_id: str,
    query_date: str,
    request: Request,
    response: Response,
    db:AsyncSession = Depends(get_db),
    Auth_token = Header(title=AuthTokenHeaderKey),
    limit: int = 10,
    offset: int = 0
):
    try:
        user: MemberProfileCurr = request.user
        
        ques = await db.get(DailyQues, post_id)
        if not ques:
            raise Exception(DAILY_QUES_NOT_FOUND)
        
        query_date = datetime.strptime(query_date, '%Y-%m-%d').date()
        
        posts = await club_daily_post_answers(db, post_id, query_date, limit, offset)

        res_posts = []
        
        for _post in posts:
            
            post = _post[0]
            
            member = {}

            _curr = PostStatusCurr(
                is_anonymous= post.is_anonymous,
            )
            member = get_member_dict_for_post_detail(_curr, image=_post[2], alias= _post[1], user_id= post.member_id)

            res_posts.append(PostAnsResponse(
                post_id = str(post.id),
                member= member,
                
                type= PostType.Answer,
                
                title= ques.title,
                body= post.answer,
                
                post_ques_id=str(post.ques_id),
                is_for_daily= True,
                
                post_at= post.post_at
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
        
        posts = await get_random_posts(db, RandomSample._50, RandomSample._10, limit)

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
    "/image/listing/"
)
async def daily_read_page_images(
    request: Request,
    response: Response,
    db:AsyncSession = Depends(get_db),
):
    try:
        
        _list = []
        for i in range(0,5):
            _list.append("downloaded_image_" + str(i) + ".jpg")
            
        curr_dir = os.getcwd()
        
        image_urls = [f"{image}" for image in _list if os.path.isfile(os.path.join(curr_dir, image))]

        red = await Redis(db = REDIS_DB)
        images_urls = await red.lrange('images_urls', 0, -1)
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
            "images": images_urls
            }

        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc),
            ResponseKeys.DATA: None
        }
        
@router.get(
    "/image/{image_name}/"
)
async def get_image(
    image_name: str
):
    curr_dir = os.getcwd()
    print(curr_dir + "---" + image_name)
    image_path = os.path.join(curr_dir, image_name)
    print(image_path)
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)