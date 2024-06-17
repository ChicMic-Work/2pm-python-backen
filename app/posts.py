from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import (
    create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, 
    create_draft_blog_post_crud, create_draft_poll_post_crud, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items
)
from crud.c_posts_list import get_member_dict_for_post_detail, get_post_tags_list
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from utilities.constants import (
    DAILY_QUES_NOT_FOUND, DRAFT_CREATED, POST_CREATED, 
    QUES_NOT_FOUND, AuthTokenHeaderKey, PostType, ResponseKeys
)

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostAnsResponse,
    PostBlogDraftRequest,
    PostBlogQuesResponse,
    # PostCreateRequest,
    PostBlogRequest,
    PostPollDraftRequest,
    PostPollRequest,
    PostPollResponse,
    PostQuesDraftRequest,
    PostQuesRequest
)

from database.models import (
    DailyQues, MemberProfileCurr, Post,
    PostDraft, PostStatusCurr
)


router = APIRouter(
    prefix='/posts',
    tags=['posts'],
)


#BLOG
@router.post(
    "/create/blog/"
    )
async def create_blog_post(
    request: Request,
    post_request: PostBlogRequest,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user
            
            del_query, post, post_curr, post_hist = await create_blog_post_crud(db, user.id, post_request.draft_id, post_request)

            db.add(post)
            db.add(post_curr)
            db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
            
            msg = POST_CREATED
            
            tags = get_post_tags_list(post)
            
            member = get_member_dict_for_post_detail(post_curr, user)

            res_data = PostBlogQuesResponse(
                post_id = str(post.id),
                member= member,
                
                title= post.title,
                body= post.body,
                type= post.type,
                
                interest_area_id= post.interest_id,
                language_id= post.lang_id,
                
                post_at= post.post_at,
                tags= tags
            )
            
            return {
                ResponseKeys.MESSAGE : msg,
                ResponseKeys.DATA: res_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/blog/"
    )
async def create_draft_blog_post(
    request: Request,
    response: Response,
    draft_request: PostBlogDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user
        
        draft = await create_draft_blog_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#QUESTION
@router.post(
    "/create/question/"
)
async def create_question_post(
    request: Request,
    response: Response,
    post_request: PostQuesRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user

            del_query, post, post_curr, post_hist = await create_ques_post_crud(db, user.id, post_request.draft_id, post_request)

            db.add(post)
            db.add(post_curr)
            db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
                
            tags = get_post_tags_list(post)
            
            member = get_member_dict_for_post_detail(post_curr, user)

            res_data = PostBlogQuesResponse(
                post_id = str(post.id),
                member= member,
                
                title= post.title,
                body= post.body,
                type= post.type,
                
                interest_area_id= post.interest_id,
                language_id= post.lang_id,
                
                post_at= post.post_at,
                tags= tags
            )
            
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: res_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/question/"
    )
async def create_draft_question_post(
    request: Request,
    response: Response,
    draft_request: PostQuesDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        draft = await create_draft_ques_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#ANSWER
@router.post(
    "/create/answer/"
    )
async def create_answer_post(
    request: Request,
    response: Response,
    post_request: PostAnsRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user

            ques  = await db.get(DailyQues, post_request.post_ques_id)
            if not ques and post_request.is_for_daily:
                raise Exception(DAILY_QUES_NOT_FOUND)
            if ques and not post_request.is_for_daily:
                post_request.is_for_daily = True
                
            if not post_request.is_for_daily:
                ques = await db.get(Post, post_request.post_ques_id)
                if not ques:
                    raise Exception(QUES_NOT_FOUND)
            
            del_query, post, post_curr, post_hist  = await create_ans_post_crud(db, user.id, post_request.draft_id, post_request, ques)

            db.add(post)

            if post_curr:
                db.add(post_curr)
            if post_hist:
                db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
            
            post_type = PostType.Answer
            
            if post_curr:
                _curr = post_curr
            else:
                _curr = PostStatusCurr(
                    is_anonymous= post_request.is_anonymous,
                )
            
            member = get_member_dict_for_post_detail(_curr, user)
            
            req_data = PostAnsResponse(
                post_id = str(post.id),
                member= member,
                
                type= post_type,
                
                title= post_request.title,
                body= post_request.body,
                
                post_ques_id=str(post_request.post_ques_id),
                is_for_daily= post_request.is_for_daily,
                
                post_at= post.post_at
            )
            
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: req_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/answer/"
    )
async def create_draft_answer_post(
    request: Request,
    response: Response,
    draft_request: PostAnsDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        ques  = await db.get(DailyQues, draft_request.post_ques_id)
        if not ques and draft_request.is_for_daily:
            raise Exception(DAILY_QUES_NOT_FOUND)
        if ques and not draft_request.is_for_daily:
            draft_request.is_for_daily = True

        if not draft_request.is_for_daily:
            ques = await db.get(Post, draft_request.post_ques_id)
            if not ques:
                raise Exception(QUES_NOT_FOUND)
        
        draft = await create_draft_ans_post_crud(db, user.id, draft_request.draft_id, draft_request, ques)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#POLL
@router.post(
    "/create/poll/"
    )
async def create_poll_post(
    request: Request,
    response: Response,
    post_request: PostPollRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    
        try:
            async with db.begin_nested():
                user: MemberProfileCurr = request.user
                
                del_queries, post, post_curr, post_hist, ques_list = await create_poll_post_crud(db, user.id, post_request.draft_id, post_request)
                
                db.add(post)
                db.add(post_curr)
                db.add(post_hist)
                db.add_all(ques_list)

                if post_request.draft_id:
                    for del_query in del_queries:
                        await db.execute(del_query)
                
                tags = get_post_tags_list(post)
                    
                member = get_member_dict_for_post_detail(post_curr, user)
                
            async with db.begin_nested():
                
                poll = await get_poll_post_items(db, post.id)
                
                req_data = PostPollResponse(
                    post_id = str(post.id),
                    member= member,
                    
                    type= post.type,
                    title= post.title,
                    body= post.body,
                    
                    tags= tags,
                    interest_area_id= post.interest_id,
                    language_id= post.lang_id,
                    
                    post_at= post.post_at,
                    poll= poll
                )

                await db.commit()
                
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: req_data
            }

        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/poll/"
    )
async def create_draft_poll_post(
    request: Request,
    response: Response,
    draft_request: PostPollDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        del_query, draft, ques_list = await create_draft_poll_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        if draft_request.draft_id:
            await db.execute(del_query)
        db.add_all(ques_list)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }


