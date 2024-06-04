from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import create_blog_post_crud, create_draft_blog_post_crud
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from utilities.constants import (
    AuthTokenHeaderKey, PostType
)

from schemas.s_posts import (
    PostBlogDraftRequest,
    PostCreateRequest,
    PostBlogRequest
)

from database.models import (
    MemberProfileCurr, Post,
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
            
            if post_request.draft_id:
                pass
            else:
                post_request = create_blog_post_crud(db, user.id, post_request)
                db.add(post_request)
                
            msg = "Post created"
            
            
            # db.commit()
                
            return {
                "message": msg,
            }
        
        except Exception as exc:
            db.rollback()
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
        
        if draft_request.draft_id:
            pass
        else:
            draft_request = create_draft_blog_post_crud(db, user.id, draft_request)
            db.add(draft_request)
        
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
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    pass


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