from pydantic import (
    BaseModel, EmailStr,
    NaiveDatetime, Field         
)
from typing import List, Optional
from schemas.s_choices import (
    LangIAResponse
)
from utilities.constants import SocialType

from uuid import UUID

class Token(BaseModel):
    access_token:str
    token_type:str

class RefreshToken(Token):
    refresh_token:str

class MemberSignup(BaseModel):
    social_id: str
    social_type: int = Field(..., ge=SocialType.Google, le=SocialType.Apple) 
    token: str
    device_type: str
    device_model: str

class MemberSignupResponse(BaseModel):
    id: UUID
    token: str

