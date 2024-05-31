from pydantic import (
    BaseModel, EmailStr,
    NaiveDatetime, Field         
)
from typing import List, Optional
from schemas.s_choices import (
    LangIAResponse, 
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

class MemberProfileAuthResponse(BaseModel):
    alias: str = None
    bio: str = None
    google_id: str| None = None
    apple_id: str| None = None
    is_dating: bool = True
    gender: str = None
    image: str | None = None
    language_choices: List[LangIAResponse] | None= []
    interest_area_choices: List[LangIAResponse] | None = []

class MemberSignupResponse(BaseModel):
    token: str
    new_user: bool
    profile: MemberProfileAuthResponse | None

