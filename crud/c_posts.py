from sqlalchemy import select, asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7
import database.models as models

from typing import List

from utilities.constants import (
    current_time, ChoicesType
)

from fastapi import HTTPException
from starlette import status

from schemas.s_posts import (
    PostCreateRequest
)

from utilities.constants import (
    PostType
)

from database.models import Post
from uuid_extensions import uuid7

async def create_post_crud(
    db: AsyncSession,
    member_id: UUID,
    post_request: PostCreateRequest
):
    if post_request.type == PostType.B:
        return Post(
            id = uuid7,
            member_id = member_id,
            intrst_id = post_request.interest_area_id,
            lang_id   = post_request.language_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
            body = post_request.body
        )
    elif post_request.type == PostType.Q:
        return Post(
            id = uuid7,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
            body = post_request.body
        )
    elif post_request.type == PostType.A:
        return Post(
            id = uuid7,
            member_id = member_id,
            ass_post_id = post_request.ass_post_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            body = post_request.body
        )
    elif post_request.type == PostType.P:
        Post(
            id = uuid7,
            member_id = member_id,
            is_anonymous = post_request.is_anonymous,
            is_drafted   = post_request.is_drafted,
            type = post_request.type,
            title = post_request.title,
        )