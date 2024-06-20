from pydantic import (
    BaseModel, Field, AwareDatetime, field_validator
)

from typing import (
    List
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
    reason_text: str | None
    content_type: str
    content: str | None
    
    @field_validator('text')
    def check_reason_text(cls, v):
        
        if v is None and cls.reason != 8:
            raise ValueError(REPORT_REASON_REQUIRED)
        return v
    
    @field_validator('content_type')
    def check_content_type(cls, v):
        
        if v not in ReportType._list:
            raise ValueError(INVALID_REPORT_TYPE)
        return v
    
    @field_validator('content')
    def check_content(cls, v):
        
        if v is None and cls.content_type == ReportType.MESSAGE:
            raise ValueError(REPORT_CONTENT_REQUIRED)
        return v