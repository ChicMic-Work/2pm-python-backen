from pydantic import (
    BaseModel, Field,
    field_validator, AwareDatetime
)
from typing import List, Optional, Union
from utilities.constants import (
    PostType, TableCharLimit
)


class PostQuestionResponse(BaseModel):
    
    post_id: str
    
    type: str = Field(default= PostType.Question, description="Question post")
    title: str = Field(..., max_length=TableCharLimit.post_title, description="Title of the question")
    body: str = Field(..., max_length=TableCharLimit.post_detail, description="Body of the question")
    
    member: dict
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int
    
    post_at: AwareDatetime


class QuesAnsListResponse(BaseModel):
    
    post_id: str
    member: dict
    
    type: str
    title: str
    body: str
    
    post_at: AwareDatetime
    

class MemberPollResult(BaseModel):
    
    poll_item_id: str