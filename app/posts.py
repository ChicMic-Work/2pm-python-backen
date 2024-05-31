from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from utilities.constants import (
    AuthTokenHeaderKey, PostType
)

from schemas.s_posts import (
    PostCreateRequest
)

router = APIRouter(
    prefix='/posts',
    tags=['posts'],
)


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