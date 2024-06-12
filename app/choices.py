from crud.c_choices import (
    create_interest_choices,
    create_language_choices,
    get_all_created_choices
)

from schemas.s_choices import (
    LangIACreate, LangIAResponse,
    ChoicesCreate
)

from database.models import (
    Languages, InterestAreas
)

from utilities.constants import (
    ChoicesType,
    ResponseKeys,
    ResponseMsg
)

from typing import (
    List
)

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db

router = APIRouter(
    prefix='/choices',
    tags=['choices'],
)


@router.post(
    "/create/",
    status_code = status.HTTP_201_CREATED
    )
async def create_choices(
    request: Request,
    choices: ChoicesCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        try:
            if choices.type == ChoicesType.Language:
                created_choices = await create_language_choices(db, choices.lang_ia)
            else:
                created_choices = await create_interest_choices(db, choices.lang_ia)

            db.add_all(created_choices)

            return ResponseMsg.CREATED

        except Exception as e:
            await db.rollback()
                
            response.status_code = status.HTTP_400_BAD_REQUEST

            return {
                ResponseKeys.MESSAGE: str(e)
            }
    
@router.get(
    "/all", 
    response_model = List[LangIAResponse],
    status_code = status.HTTP_200_OK
    )
async def get_all_choices(
    request: Request,
    type: int,
    db: AsyncSession = Depends(get_db)
):
    choices = await get_all_created_choices(db, type)
    return choices