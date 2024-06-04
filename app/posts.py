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
    create_ques_post_crud, create_draft_ques_post_crud
)
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from utilities.constants import (
    AuthTokenHeaderKey, PostType
)

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostBlogDraftRequest,
    # PostCreateRequest,
    PostBlogRequest,
    PostPollRequest,
    PostQuesDraftRequest,
    PostQuesRequest
)

from database.models import (
    DailyQues, MemberProfileCurr, Post,
    PostDraft
)


router = APIRouter(
    prefix='/posts',
    tags=['posts'],
)

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

            await db.execute(del_query)
            
            msg = "Post created"

            return {
                "message": msg,
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": str(exc)
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

        return {
            "message": "Draft created"
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc)
        }


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

            await db.execute(del_query)
                
            msg = "Post created"
                
            return {
                "message": msg,
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": str(exc)
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

        return {
            "message": "Draft created"
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc)
        }


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

            daily_ques  = await db.get(DailyQues, post_request.post_ques_id)
            if not daily_ques and post_request.is_for_daily:
                raise Exception("Daily question not found")
            if daily_ques and not post_request.is_for_daily:
                post_request.is_for_daily = True
            
            del_query, post, post_curr, post_hist  = await create_ans_post_crud(db, user.id, post_request.draft_id, post_request)

            db.add(post)

            if post_curr:
                db.add(post_curr)
            if post_hist:
                db.add(post_hist)

            await db.execute(del_query)
                
            msg = "Post created"
                
            return {
                "message": msg,
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": str(exc)
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

        daily_ques  = await db.get(DailyQues, draft_request.post_ques_id)
        if not daily_ques and draft_request.is_for_daily:
            raise Exception("Daily question not found")
        if daily_ques and not draft_request.is_for_daily:
            draft_request.is_for_daily = True

        draft = await create_draft_ans_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        db.commit()

        return {
            "message": "Draft created"
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc)
        }


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
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            del_queries, post, post_curr, post_hist, ques_list = await create_poll_post_crud(db, user.id, post_request.draft_id, post_request)
            
            db.add(post)
            db.add(post_curr)
            db.add(post_hist)
            db.add_all(ques_list)

            for del_query in del_queries:
                await db.execute(del_query)
            
            msg = "Post created"
            
            return {
                "message": msg,
            }

        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": str(exc)
            }


@router.post(
    "/draft/poll/"
    )
async def create_draft_poll_post(
    request: Request,
    response: Response,
    draft_request: PostPollRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        del_query, draft, ques_list = await create_draft_poll_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        await db.execute(del_query)
        db.add_all(ques_list)
        db.commit()

        return {
            "message": "Draft created"
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc)
        }

"""
@router.post(
    "/create/"
    )
async def create_post(
    request: Request,
    post_request: PostCreateRequest,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        request.user
        if post_request.type == PostType.B:
            pass
            # TODO: Create blog
            # need title, body
            
        elif post_request.type == PostType.Q:
            pass
            # TODO: Create quest
            # req: body, title
        elif post_request.type == PostType.A:
            pass
            # TODO: Create answer
            # req: asso, body
        elif post_request.type == PostType.P:
            pass
            # TODO: Create Poll
            # req: asso, title
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": f"invalid post type: {post_request.type}"
            }
        
            
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc)
        }

"""