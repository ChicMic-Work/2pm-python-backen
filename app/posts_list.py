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
from crud.c_posts_list import get_ans_drafts, get_blog_drafts, get_poll_drafts, get_ques_drafts
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
    DailyQues, MemberProfileCurr, Post,
    PostDraft
)

from app.posts import router

# router = APIRouter(
#     prefix='/drafts',
#     tags=['drafts'],
# )

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
        
        if post_draft.type == PostType.Blog:
            
            tags = []
            
            
            post_draft = PostBlogQuesResponse(
                post_id = str(post_draft.id),
                member= {"alias": user.alias},
                
                title= post_draft.title,
                body= post_draft.body,
                type= post_draft.type,
                
                interest_area_id= post_draft.interest_id,
                language_id= post_draft.lang_id,
                
                post_at= post_draft.post_at,
                tags= tags
            )
        elif post_draft.type == PostType.Question:
            post_draft = PostQuesDraftRequest
        elif post_draft.type == PostType.Answer:
            post_draft = PostAnsDraftRequest
        elif post_draft.type == PostType.Poll:
            post_draft = PostPollRequest
        
        PostBlogQuesResponse
        
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