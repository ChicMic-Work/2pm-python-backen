from pydantic import (
    BaseModel, Field, AwareDatetime
)

from typing import (
    List
)
from uuid import UUID

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