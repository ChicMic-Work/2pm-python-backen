from crud.c_profile import (
    create_user_language_choices,
    create_user_interest_choices,
    get_used_alias, create_user_alias
)

from crud.c_auth import (
    get_user_by_id
)

from schemas.s_choices import (
    LangIACreate, LangIAResponse,
    ChoicesCreate
)

from schemas.s_profile import (
    MemberProfileCreate,
    MemberProfileResponse,
    ProfileImageUpload
)

from database.models import (
    Languages, InterestAreas,
    MemberProfile
)

from utilities.constants import (
    current_time, ALIAS_VALID, 
    AuthTokenHeaderKey, ALIAS_INVALID, 
    ALIAS_INVALID_CHARACTER, ALIAS_CURRENT,
    ALIAS_EXISTS, CLOUDFRONT_URL, IMAGE_FAIL
)

from utilities.common import normalize_nickname

from utilities.s3_upload import (
    upload_file, remove_file
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

from dependencies import get_db


router = APIRouter(
    prefix='/profile',
    tags=['profile'],
)


@router.post(
    "/create/"
    )
async def create_profile(
    request: Request,
    profile: MemberProfileCreate,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfile = await get_user_by_id(db, request.user.id)
        try:
            alias = normalize_nickname(profile.alias)
        except:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_INVALID_CHARACTER,
                "is_valid": False
            }
        
        if not alias or len(alias) > 20:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_INVALID,
                "is_valid": False
            }
        
        
        if user.alias and alias != user.alias and await get_used_alias(db, alias):
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_EXISTS,
                "is_valid": False
            }
        
        if user.alias and alias == user.alias:
            pass
        else:
            user.alias = alias
            mem_alias, all_alias = await create_user_alias(alias, user.id )
            db.add(mem_alias)
            db.add(all_alias)
            
        user.bio = profile.bio
        user.gender = profile.gender
        user.is_dating = profile.is_dating
        
        interests = await create_user_interest_choices(db, profile.interest_area_choices)
        languages = await create_user_language_choices(db, profile.language_choices)
        
        user.language_choices.clear()
        user.interest_area_choices.clear()
        
        user.language_choices.extend(languages)
        user.interest_area_choices.extend(interests)
        
        db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        return user
        
    except Exception as exc:
        await db.rollback()
        if hasattr(exc, "detail") and hasattr(exc, "status_code"):
            msg = exc.detail
            status_code = exc.status_code
        else:
            status_code = 500
            msg = 'Internal Server Error'

        await db.rollback()
        raise HTTPException(status_code=status_code, detail=msg) from exc
    
@router.get(
    "/user"
    )
async def get_user_profile(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    user: MemberProfile = await get_user_by_id(db, request.user.id)
    
    return user

@router.get(
    "/alias"
    )
async def get_used_aliases(
    request: Request,
    alias: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    
    try:
        alias = normalize_nickname(alias)
    except:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_INVALID_CHARACTER,
            "is_valid": False
        }
    
    if not alias or len(alias) > 20:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
                "message": ALIAS_INVALID,
                "is_valid": False
            }
    
    if request.user.alias and alias == request.user.alias:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_CURRENT,
            "is_valid": True
        }
    
    if await get_used_alias(db, alias):
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_EXISTS,
            "is_valid": False
        }
    
    return {
        "message": ALIAS_VALID,
        "is_valid": True
    }
    
@router.post(
    "/image/",
)
async def upload_profile_image(
    request: Request,
    response: Response,
    image: UploadFile = File(...),
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        db_user:MemberProfile = request.user
        if db_user.image:
            remove_file(db_user.image)
            
        contents = image.file.read()
        image.file.seek(0)
        res = upload_file(image.file, image.filename)
        
        if res:
            db_user.image = f"{CLOUDFRONT_URL}{image.filename}"
            db.add(db_user)
            await db.commit()
            return {
                "image": f"{CLOUDFRONT_URL}{image.filename}"
            }
            
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": IMAGE_FAIL,
            "exc": "image upload error"
        }
    except Exception as exc:
        db.rollback()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": IMAGE_FAIL,
            "exc": str(exc)
        }
    