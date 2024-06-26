from crud.c_posts_list import convert_all_post_list_for_response
from crud.c_profile import (
    create_alias_history,
    create_mem_profile_history,
    get_searched_users,
    get_used_alias,
    get_user_posts_details_by_user_id,
    get_user_profile_details_by_id,
)

from crud.c_auth import (
    create_reg_user_sign_in_session,
    create_signin_session,
    create_user,
    get_user_by_id
)

from crud.c_choices import (
    create_mem_languages,
    create_mem_interst_areas,
    get_mem_choices,
    get_mem_interest_areas,
    get_mem_languages
)

from crud.c_profile_actions import follow_unfollow_user, mute_unmute_user, spam_non_spam_user
from schemas.s_choices import (
    LangIACreate, LangIAResponse,
    ChoicesCreate, MemberChoicesReq
)

from schemas.s_profile import (
    MemberProfileCreate,
    MemberProfileDetailResponse,
    MemberProfileResponse,
    ProfileImageUpload,
    SearchedUserResponse
)

from database.models import (
    Languages, InterestAreas,
    MemberProfileCurr, MemberProfileHist, MemberRegistration, PostStatusCurr
)

from utilities.constants import (
    ALIAS_ATMOST, BIO_ATMOST, FOLLOWED, UNFOLLOWED, ResponseKeys, TableCharLimit, ALIAS_VALID, ALIAS_ATLEAST,
    AuthTokenHeaderKey, ALIAS_INVALID, 
    ALIAS_INVALID_CHARACTER, ALIAS_CURRENT,
    ALIAS_EXISTS, CLOUDFRONT_URL, IMAGE_FAIL,
    ChoicesType, access_token_expire
)

from utilities.common import normalize_nickname

from utilities.s3_upload import (
    upload_file, remove_file,
)

from typing import (
    List
)

from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from dependencies import create_access_token, get_db


from app.profile import router


@router.post(
    "/follow/{user_id}",
)
async def follow_user(
    user_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    Auth_token = Header(title=AuthTokenHeaderKey),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            if str(user.id) == user_id:
                raise Exception("You can't follow yourself")
            
            del_query, hist, curr = await follow_unfollow_user(db, user.id, user_id)
            
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
            }
            

@router.post(
    "/spam/{user_id}",
)
async def spam_user(
    user_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    Auth_token = Header(title=AuthTokenHeaderKey),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            if str(user.id) == user_id:
                raise Exception("You can't spam yourself")
            
            del_query, hist, curr = await spam_non_spam_user(db, user.id, user_id)
            
            if del_query:
                await db.delete(del_query)
                msg = "Removed from spam"
            else:
                db.add(curr)
                msg = "Added to spam"
                
            db.add(hist)
            
            return {
                ResponseKeys.MESSAGE: msg
            }
            
            
        except Exception as exc:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc),
            }
            

@router.post(
    "/mute/{user_id}",
)
async def mute_user(
    user_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    Auth_token = Header(title=AuthTokenHeaderKey),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            if str(user.id) == user_id:
                raise Exception("You can't mute yourself")
            
            del_query, hist, curr = await mute_unmute_user(db, user.id, user_id)
            
            if del_query:
                await db.delete(del_query)
                msg = "Removed from mute"
            else:
                db.add(curr)
                msg = "Added to mute"
                
            db.add(hist)
            
            return {
                ResponseKeys.MESSAGE: msg
            }
            
            
        except Exception as exc:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc),
            }
            
            