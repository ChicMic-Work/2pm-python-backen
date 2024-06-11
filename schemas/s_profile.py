from pydantic import (
    BaseModel, EmailStr,
    NaiveDatetime, Field,
    field_validator, ValidationError,
    AwareDatetime
)

from typing import List, Optional
from schemas.s_choices import (
    LangIAResponse
)

from database.table_keys import (
    MemberProfileKeys
)

from fastapi import UploadFile

from uuid import UUID

from utilities.constants import TableCharLimit

class ProfileImageUpload(BaseModel):
    image: UploadFile

class MemberProfileBase(BaseModel):
    alias: str
    bio: str | None = None
    is_dating: bool = True
    gender: str
    
    # @field_validator('gender')
    # def valid_gender(gender: str):
    #     if gender not in MemberProfileKeys.gender_validation:
    #         raise ValueError(f"invalid gender value: {gender}")
    #     return gender

    
class MemberProfileCreate(MemberProfileBase):
    language_choices: List[int] = []
    interest_area_choices: List[int] = []
    
class MemberProfileResponse(BaseModel):
    alias: str
    google_id: str | None = None
    apple_id: str | None= None
    apple_email: EmailStr | None = None
    google_email: EmailStr | None = None
    join_at: AwareDatetime
    bio: str | None = None
    is_dating: bool = True
    gender: str
    image: str |None = None
    language_choices: List[LangIAResponse] = []
    interest_area_choices: List[LangIAResponse] = []
    token: str|None = None
    
    
class MemberProfileDetailResponse(BaseModel):

    id: str
    alias: str

    join_at: AwareDatetime
    bio: str | None = None
    
    is_dating: bool = True
    gender: str
    image: str |None = None
    my_profile: bool = False


class SearchedUserResponse(BaseModel):
    id: UUID
    alias: str
    image: str | None = None
    bio: str | None = None