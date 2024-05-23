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
    current_time, ChoicesType
)

from typing import (
    List
)

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db

router = APIRouter(
    prefix='/choices',
    tags=['choices'],
)


@router.post(
    "/create/",
    response_model = List[LangIAResponse],
    status_code = status.HTTP_201_CREATED
    )
async def create_choices(
    request: Request,
    choices: ChoicesCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        if choices.type == ChoicesType.Language:
            created_choices = await create_language_choices(db, choices.lang_ia)
        else:
            created_choices = await create_interest_choices(db, choices.lang_ia)
            
        response_list: List[LangIAResponse] = []
        # for res in created_choices:
        #     response_list.append(LangIAResponse(
        #         id = res.id,
        #         name= res.name
        #     )) 
        
        db.add_all(created_choices)
        await db.commit()
        # for i in created_choices:
        #     aa = await db.refresh(i)
        #     response_list.append(LangIAResponse(
        #         id = aa.id,
        #         name= aa.name
        #     )) 
        return "created"

    except Exception as e:
        await db.rollback()
        if hasattr(e, "detail") and hasattr(e, "status_code"):
            msg = e.detail
            status_code = e.status_code
        else:
            status_code = 500
            msg = 'Internal Server Error'

        raise HTTPException(status_code=status_code, detail=msg) from e
    
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