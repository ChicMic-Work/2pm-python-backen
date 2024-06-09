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
from crud.c_posts_list import get_CD_answers, get_HOP_polls, get_MP_posts, get_ans_drafts, get_blog_drafts, get_member_dict_for_post_detail, get_member_poll_taken, get_poll_drafts, get_post_poll, get_post_polls_list, get_post_question, get_post_questions_list, get_post_tags_list, get_ques_drafts, get_searched_posts
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_posts_list import  PostQuestionResponse, QuesAnsListResponse
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
            raise Exception("Invalid post type")
        
        if post_type == PostType.Blog:
            drafts = await get_blog_drafts(db, user.id)
        elif post_type == PostType.Question:
            drafts = await get_ques_drafts(db, user.id)
        elif post_type == PostType.Answer:
            drafts = await get_ans_drafts(db, user.id)
        elif post_type == PostType.Poll:
            drafts = await get_poll_drafts(db, user.id)

        return {
            "message": "success",
            "data": drafts
        }

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
            raise Exception("Draft not found")
        if post_draft.member_id != user.id:
            raise Exception("Draft not found")
        
        if post_draft.type == PostType.Blog or post_draft.type == PostType.Question:
            
            tags = []
            
            
            post_draft = PostBlogQuesResponse(
                post_id = str(post_draft.id),
                member= {"alias": user.alias},
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                post_at= post_draft.save_at,
                tags= tags
            )
            
        # elif post_draft.type == PostType.Question:
        #     post_draft = PostBlogQuesResponse(
        #         post_id = str(post_draft.id),
        #         member= {"alias": user.alias},
                
        #         title= post_draft.title,
        #         body= post_draft.body,
        #         type= post_draft.type,
                
        #         interest_area_id= post_draft.interest_id,
        #         language_id= post_draft.lang_id,
                
        #         post_at= post_draft.save_at
        #     )
        elif post_draft.type == PostType.Answer:
            post_draft = PostAnsResponse(
                post_id = str(post_draft.id),
                member= {"alias": user.alias},
                
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
                member= {"alias": user.alias},
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                post_at= post_draft.save_at,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                poll= await get_poll_post_items(db, post_draft.id)
            )
        
        
        
        return {
            "message": "success",
            "data": post_draft
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
    offset: int = 0
):
    try:

        user: MemberProfileCurr = request.user
        questions = await get_post_questions_list(db, limit, offset)
        
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
            "message": "success",
            "data": res_data
        }

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
        
        # member = {
        #     "image": post[2],
        #     "alias": post[3],
        #     "is_anonymous": post[1].is_anonymous
        # }
        
        # if post[1].is_anonymous:
        #     member = {
        #         "image": None,
        #         "alias": None,
        #         "is_anonymous": post[1].is_anonymous
        #     }
        
        # PostAnsResponse(
        #     post_id = str(post.id),
        #     member= {"alias": user.alias},
        #     type= post.type,
        #     title= post.title,
        #     body= post.body,
        #     post_at= post.post_at,
        #     ans_list= ans_list
        # )
        
        return {
            "message": "success",
            "data": {"ans_list": ans_list}
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
    offset: int = 0
):
    try:

        user: MemberProfileCurr = request.user
        polls = await get_post_polls_list(db, limit, offset)
        
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
            "message": "success",
            "data": res_data
        }
        
                
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
        
        post, poll_items = await get_post_poll(db, post_id)
        
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
            "message": "success",
            "data": {
                "poll": poll_data,
                "reveal_at": poll_reveal,
                "selected_choices": mem_poll
            }
        }
                    
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
        }
        
        
@router.get(
    "/HOP/"
)
async def hot_off_press(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_HOP_polls(db, limit, offset)

        res_posts = []
        
        for post in posts:
            
            member = get_member_dict_for_post_detail(post[1], image=post[2], alias= post[3])

            if post[0].type == PostType.Question or post[0].type == PostType.Blog:

                tags = get_post_tags_list(post[0])

                res_posts.append(PostBlogQuesResponse(
                    post_id = str(post[0].id),
                    member= member,

                    title= post[0].title,
                    body= post[0].body,
                    type= post[0].type,

                    interest_area_id= post[0].interest_id,
                    language_id= post[0].lang_id,

                    post_at= post[0].post_at,
                    tags= tags
                ))
            elif post[0].type == PostType.Answer:

                res_posts.append(PostAnsResponse(
                    post_id = str(post[0].id),
                    member= member,
                    
                    type= post[0].type,
                    
                    title= post[0].title,
                    body= post[0].body,
                    
                    post_ques_id=str(post[0].post_ques_id),
                    is_for_daily= False,
                    
                    post_at= post[0].post_at
                ))

            elif post[0].type == PostType.Poll:

                tags = get_post_tags_list(post[0])

                res_posts.append(PostPollResponse(
                    post_id = str(post[0].id),
                    member= member,
                    
                    type= post[0].type,
                    title= post[0].title,
                    body= post[0].body,
                    
                    tags= tags,
                    interest_area_id= post[0].interest_id,
                    language_id= post[0].lang_id,
                    
                    post_at= post[0].post_at
                ))


        return {
            "message": "success",
            "data": res_posts.reverse()
        }
                

    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
        }
    

@router.get(
    "/CD/"
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
        
        posts = await get_CD_answers(db, limit, offset)
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
            "message": "success",
            "data": res_posts
        }
    
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
        }
    

@router.get(
    "/MP/"
)
async def most_popular_posts(
    request: Request,
    response: Response,
    # Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    interest: int = None
):
    try:
        user: MemberProfileCurr = request.user
        
        posts = await get_MP_posts(db, limit, offset, interest)

        res_posts = []
        
        for post in posts:
            
            member = get_member_dict_for_post_detail(post[2], image=post[3], alias= post[4])

            if post[1].type == PostType.Question or post[1].type == PostType.Blog:

                tags = get_post_tags_list(post[1])

                res_posts.append(PostBlogQuesResponse(
                    post_id = str(post[1].id),
                    member= member,

                    title= post[1].title,
                    body= post[1].body,
                    type= post[1].type,

                    interest_area_id= post[1].interest_id,
                    language_id= post[1].lang_id,

                    post_at= post[1].post_at,
                    tags= tags
                ))
            elif post[1].type == PostType.Answer:

                res_posts.append(PostAnsResponse(
                    post_id = str(post[1].id),
                    member= member,
                    
                    type= post[1].type,
                    
                    title= post[1].title,
                    body= post[1].body,
                    
                    post_ques_id=str(post[1].post_ques_id),
                    is_for_daily= False,
                    
                    post_at= post[1].post_at
                ))

            elif post[1].type == PostType.Poll:

                tags = get_post_tags_list(post[1])

                res_posts.append(PostPollResponse(
                    post_id = str(post[1].id),
                    member= member,
                    
                    type= post[1].type,
                    title= post[1].title,
                    body= post[1].body,
                    
                    tags= tags,
                    interest_area_id= post[1].interest_id,
                    language_id= post[1].lang_id,
                    
                    post_at= post[1].post_at
                ))

        return {
            "message": "success",
            "data": res_posts
        }
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
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
        
        posts = await get_searched_posts(db, search, limit, offset)

        res_posts = []
    
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
        }