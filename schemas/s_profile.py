from pydantic import (
    BaseModel, EmailStr,
    NaiveDatetime, Field,
    field_validator, ValidationError
         
)

from typing import List, Optional
from schemas.s_choices import (
    LangIAResponse
)

from database.table_keys import (
    MemberProfileKeys
)

from uuid import UUID

class MemberProfileBase(BaseModel):
    alias: str
    bio: str = None
    image: str = "abc"
    gender: str
    
    @field_validator('gender')
    def valid_gender(gender: str):
        if gender not in MemberProfileKeys.gender_validation:
            raise ValueError(f"invalid gender value: {gender}")
        return gender
    
    
class MemberProfileCreate(MemberProfileBase):
    language_choices: List[UUID] = []
    interest_area_choices: List[UUID] = []
    
class MemberProfileResponse(MemberProfileBase):
    language_choices: List[LangIAResponse] = []
    interest_area_choices: List[LangIAResponse] = []