from pydantic import BaseModel, field_validator
from uuid import UUID

from utilities.constants import (
    PostType
)

from typing import List

class PostCreateRequest(BaseModel):
    
    type: str
    
    is_anonymous: bool
    is_drafted: bool
    
    title: str = None
    body: str = None
    tags: List[str] = []
    
    interest_area_id: UUID = None
    language_id: UUID = None
    
    ass_post_id: UUID = None
    
    @field_validator('type')
    def valid_type(self, type: str):
        if self.type not in PostType.types_list:
            raise ValueError(f"invalid post type: {type}")
    
    @field_validator('ass_post_id')
    def valid_ass_post_id(self):
        if  self.type == PostType.A and self.ass_post_id == None:
            raise ValueError(f"For answer associated post can't be null")
        
    @field_validator('title')
    def valid_title(self):
        if self.type != PostType.A and self.title == None:
            raise ValueError(f"Provide title for post")
        
    @field_validator('body')
    def valid_body(self):
        if (self.type != PostType.A or self.type != PostType.P) and self.body == None:
            raise ValueError(f"Provide body for post")
    
    @field_validator('interest_area_id')
    def valid_interest_area_id(self):
        if self.type == PostType.B and (self.interest_area_id == None or self.language_id == None):
            raise ValueError(f"Provide interest_area_id and language_id for blog post")