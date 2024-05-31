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
    ChoicesCreate, MemberChoicesReq
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
    current_time, ALIAS_VALID, ALIAS_ATLEAST,
    AuthTokenHeaderKey, ALIAS_INVALID, 
    ALIAS_INVALID_CHARACTER, ALIAS_CURRENT,
    ALIAS_EXISTS, CLOUDFRONT_URL, IMAGE_FAIL,
    ChoicesType
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
    "/create/",
    # response_model= MemberProfileResponse
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
            normalized_alias = normalize_nickname(profile.alias)
        except:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_INVALID_CHARACTER,
                "is_valid": False
            }
            
        
        
        if not profile.alias or len(profile.alias) > 20 or not normalized_alias:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_ATLEAST,
                "is_valid": False
            }
        
        
        if user.alias and profile.alias != user.alias and await get_used_alias(db, normalized_alias):
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_EXISTS,
                "is_valid": False
            }
        
        if user.alias and profile.alias == user.alias:
            pass
        else:
            user.alias = profile.alias
            mem_alias, all_alias = await create_user_alias(profile.alias, normalized_alias, user.id )
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
        
        language_choices = []
        interest_area_choices = []
        
        for lang in user.language_choices:
            language_choices.append(
                LangIAResponse(
                    id = lang.id,
                    name = lang.name,
                    create_date= lang.create_date
                )
            )
        
        for intr in user.interest_area_choices:
            interest_area_choices.append(
                LangIAResponse(
                    id = intr.id,
                    name = intr.name,
                    create_date= intr.create_date
                )
            )
        
        return MemberProfileResponse(
            alias= user.alias,
            bio= user.bio,
            google_id= user.google_id,
            apple_id= user.apple_id,
            is_dating= user.is_dating,
            image= user.image,
            gender= user.gender,
            language_choices= language_choices,
            interest_area_choices= interest_area_choices
        )
        
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
        normalized_alias = normalize_nickname(alias)
    except:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_INVALID_CHARACTER,
            "is_valid": False
        }
    
    if not alias or len(alias) > 20 or not normalized_alias:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
                "message": ALIAS_ATLEAST,
                "is_valid": False
            }
    
    if request.user.alias and alias == request.user.alias:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_CURRENT,
            "is_valid": True
        }
    
    if await get_used_alias(db, normalized_alias):
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
 
@router.delete(
    "/image/",
)
async def delete_profile_image(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        
        db_user:MemberProfile = request.user
        if db_user.image:
            remove_file(db_user.image)
            db_user.image = None
            db.add(db_user)
            await db.commit()
        
        return {
            "image": None
        }
            
    except Exception as exc:
        db.rollback()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": IMAGE_FAIL,
            "exc": str(exc)
        }
        
@router.post(
    "/choices/",
)
async def member_languages(
    request: Request,
    response: Response,
    lang_ia: MemberChoicesReq,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db)
):
    try:
        user: MemberProfile = await get_user_by_id(db, request.user.id)
        
        if lang_ia.type == ChoicesType.Language:
            languages = await create_user_language_choices(db, lang_ia.lang_ia)
            user.language_choices.clear()
            user.language_choices.extend(languages)
            return_lang = True
        else:
            interests = await create_user_interest_choices(db, lang_ia.lang_ia)
            user.interest_area_choices.clear()
            user.interest_area_choices.extend(interests)
            return_lang = False
            
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        if return_lang:
            return user.language_choices
        return user.interest_area_choices
        
        # return {
        #     "message": "Created user choices"
        # }
    except Exception as exc:
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": str(exc)
        }