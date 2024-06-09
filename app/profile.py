from crud.c_profile import (
    create_alias_history,
    create_mem_profile_history,
    get_searched_users,
    get_used_alias,
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
    MemberProfileCurr, MemberProfileHist, MemberRegistration
)

from utilities.constants import (
    ALIAS_ATMOST, BIO_ATMOST, TableCharLimit, ALIAS_VALID, ALIAS_ATLEAST,
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


router = APIRouter(
    prefix='/profile',
    tags=['profile'],
)


@router.post(
    "/create/",
    )
async def create_profile(
    request: Request,
    profile: MemberProfileCreate,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):

    try:
        try:
            request.user.__getattribute__("reg_user")
            user: MemberRegistration = request.user
            reg_user = True
        except:
            user: MemberProfileCurr = request.user
            reg_user = False


        try:
            normalized_alias = normalize_nickname(profile.alias)
        except:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_INVALID_CHARACTER,
                "is_valid": False
            }
            
        if len(profile.alias) > TableCharLimit.alias:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_ATMOST,
                "is_valid": False
            }
        
        if profile.bio and len(profile.bio) > TableCharLimit.bio:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": BIO_ATMOST,
            }
        
        if not profile.alias or not normalized_alias:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_ATLEAST,
                "is_valid": False
            }
        
        used_alias = await get_used_alias(db, normalized_alias)
        
        if profile.alias != user.alias and used_alias:
            response.status_code= status.HTTP_400_BAD_REQUEST
            return {
                "message": ALIAS_EXISTS,
                "is_valid": False
            }
        

        if user.alias and user.alias == profile.alias:
            pass
        else:
            user.alias = profile.alias
            user.alias_std = normalized_alias
            all_alias = await create_alias_history(normalized_alias)
            db.add(all_alias)
        
        user.bio = profile.bio
        user.is_dating = profile.is_dating
        user.gender = profile.gender
        user.update_at = func.now()
        
        if reg_user:
            del_query, user, new_profile = await create_user(db, user)
            ip = None
            if request.client.host:
                ip = request.client.host
            session = create_reg_user_sign_in_session(
                user.id,
                ip,
                request.user.__getattribute__("social_id"),
                request.user.__getattribute__("device_type"),
                request.user.__getattribute__("device_model"),
                request.user.__getattribute__("type")
            )
            add_query_l = await create_mem_languages(db, user.id, profile.language_choices, False)
            add_query_i = await create_mem_interst_areas(db, user.id, profile.interest_area_choices, False)
            db.add_all(add_query_i)
            db.add_all(add_query_l)
            db.add(session)
            access_token = await create_access_token(user.id, session.id, access_token_expire)

        else:
            new_profile = await create_mem_profile_history(user)
            access_token = None

        db.add(user)
        db.add(new_profile)
        if reg_user:
            await db.execute(del_query)
        await db.commit()
        await db.refresh(user)

        lang_list, int_list = await get_mem_choices(db, user.id)

        return MemberProfileResponse(
            alias= user.alias,
            bio= user.bio,
            google_id= user.google_id,
            apple_id= user.apple_id,
            apple_email = user.apple_email,
            google_email = user.google_email,
            join_at= user.join_at,
            is_dating= user.is_dating,
            image= user.image,
            gender= user.gender,
            language_choices= lang_list,
            interest_area_choices= int_list,
            token= access_token
        )
        
    except Exception as exc:
        
        await db.rollback()

        raise HTTPException(status_code= 500, detail= str(exc)) from exc
    
@router.get(
    "/user",
    )
async def get_user_profile(
    request: Request,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    user: MemberProfileCurr = request.user
    
    lang_list, int_list = await get_mem_choices(db, user.id)

    return MemberProfileResponse(
        alias= user.alias,
        bio= user.bio,
        google_id= user.google_id,
        apple_id= user.apple_id,
        apple_email = user.apple_email,
        google_email = user.google_email,
        join_at= user.join_at,
        is_dating= user.is_dating,
        image= user.image,
        gender= user.gender,
        language_choices= lang_list,
        interest_area_choices= int_list
        )

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
    
    if not alias:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_ATLEAST,
            "is_valid": False
        }


    if len(alias) > 20:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_ATMOST,
            "is_valid": False
        }
    
    try:
        normalized_alias = normalize_nickname(alias)
    except:
        response.status_code= status.HTTP_400_BAD_REQUEST
        return {
            "message": ALIAS_INVALID_CHARACTER,
            "is_valid": False
        }
    
    if not normalized_alias:
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
    async with db.begin(): 
        try:
            db_user:MemberProfileCurr = request.user
            if db_user.image:
                remove_file(db_user.image)
                
            contents = image.file.read()
            image.file.seek(0)
            res = upload_file(image.file, image.filename)
            
            if res:
                db_user.image = f"{CLOUDFRONT_URL}{image.filename}"
                db.add(db_user)
                return {
                    "image": f"{CLOUDFRONT_URL}{image.filename}"
                }
                
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "message": IMAGE_FAIL,
                "exc": "image upload error"
            }
        except Exception as exc:
            await db.rollback()
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
    async with db.begin(): 
    
        try:
            
            db_user:MemberProfileCurr = request.user
            if db_user.image:
                remove_file(db_user.image)
                db_user.image = None
                db.add(db_user)
            
            return {
                "image": None
            }
                
        except Exception as exc:
            await db.rollback()
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
            user: MemberProfileCurr = request.user
            
            async with db.begin():
                if lang_ia.type == ChoicesType.Language:
                    add_query = await create_mem_languages(db, user.id, lang_ia.lang_ia, True)
                    return_lang = True
                else:
                    add_query = await create_mem_interst_areas(db, user.id, lang_ia.lang_ia, True)
                    return_lang = False
                    
                db.add_all(add_query)
            
            async with db.begin_nested():
                if return_lang:
                    lang_ia = await get_mem_languages(db, user.id) 
                else:
                    lang_ia = await get_mem_interest_areas(db, user.id)

                lang_list = []
                if lang_ia:
                    for i in lang_ia:
                        lang_list.append(LangIAResponse(
                            id = i[0],
                            name = i[1],
                            add_date= i[2]
                        ))

                return lang_list
            
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {
                "message": str(exc)
            }
        

@router.get(
    "/get/users/",
)
async def search_users(
    request: Request,
    response: Response,
    name: str,
    limit: int = 10,
    offset: int = 0,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        users = await get_searched_users(db, name, limit, offset)
        
        return {
            "message": "success",
            "data": users
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(exc),
            "data": None
        }