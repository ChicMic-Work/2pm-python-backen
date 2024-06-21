from pydantic import (
    BaseModel, Field, AwareDatetime, field_validator, model_validator
)

from typing import (
    List, Optional
)
from uuid import UUID

from utilities.constants import INVALID_REPORT_TYPE, REPORT_CONTENT_REQUIRED, REPORT_REASON_REQUIRED, ReportType

class MemTakePollReq(BaseModel):
    poll_item_ids: List[UUID] 
    
class MemInviteListBase(BaseModel):
    
    
    id: UUID
    alias: str
    image: str | None
    
    followers_count: int
    following_count: int
    
    invite_at: AwareDatetime   
    

class MemInvSentList(MemInviteListBase):
    
    answer_id: UUID | None


class ReportReasonReq(BaseModel):
    reason: int = Field(..., ge=1, le=8)
    reason_text: Optional[str]
    content_type: str
    content: Optional[str]

    @model_validator(mode="before")
    def validate_fields(cls, values):
        reason = values.get('reason')
        reason_text = values.get('reason_text')
        content_type = values.get('content_type')
        content = values.get('content')
        
        if reason != 8 and not reason_text:
            raise ValueError("REPORT_REASON_REQUIRED")
        
        if content_type not in ReportType._list:
            raise ValueError("INVALID_REPORT_TYPE")
        
        if content_type == ReportType.MESSAGE and not content:
            raise ValueError("REPORT_CONTENT_REQUIRED")
        
        return values

"""
class ReportReasonReq(BaseModel):
    
    reason: int = Field(..., ge=1, le=8)
    reason_text: str | None
    content_type: str
    content: str | None
    
    @field_validator('text')
    def validate_text(cls, v):
        
        if v is None and cls.reason != 8:
            raise ValueError(REPORT_REASON_REQUIRED)
        return v
    
    @field_validator('content_type')
    def validate_content_type(cls, v):
        
        if v not in ReportType._list:
            raise ValueError(INVALID_REPORT_TYPE)
        return v
    
    @field_validator('content')
    def validate_content(cls, v):
        
        if v is None and cls.content_type == ReportType.MESSAGE:
            raise ValueError(REPORT_CONTENT_REQUIRED)
        return v
        
"""