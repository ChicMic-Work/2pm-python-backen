from pydantic import BaseModel, field_validator, Field
from uuid import UUID

from utilities.constants import (
    PostType, TableCharLimit
)

from typing import List, Optional, Union

    
class PostBlogRequest(BaseModel):
    type: str = Field(..., default= PostType.Blog, description="Type of the blog post")
    
    title: str = Field(..., max_length=TableCharLimit.post_title, description="Title of the blog post")
    body: str = Field(..., max_length=TableCharLimit.post_detail, description="Body of the blog post")
    
    draft_id: Optional[UUID]
    is_anonymous: bool
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int

    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Blog:
            raise ValueError('type must be B')
        return v
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 3:
            raise ValueError('There can be up to 3 tags')
        for tag in v:
            # if isinstance(tag, str) and len(tag) > TableCharLimit.tag:
            #     raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
            if len(tag) > TableCharLimit.tag:
                raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
        return v

class PostBlogDraftRequest(BaseModel):
    type: str = Field(..., default= PostType.Blog, description="Type of the blog post")
    
    title: str | None = Field(max_length=TableCharLimit.post_title, description="Title of the blog post")
    body: str | None = Field(max_length=TableCharLimit.post_detail, description="Body of the blog post")
    
    draft_id: Optional[UUID]
    
    is_anonymous: bool
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int
    
    

    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Blog:
            raise ValueError('type must be B')
        return v
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 3:
            raise ValueError('There can be up to 3 tags')
        for tag in v:
            # if isinstance(tag, str) and len(tag) > TableCharLimit.tag:
            #     raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
            if len(tag) > TableCharLimit.tag:
                raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
        return v

class PostQuesRequest(BaseModel):
    type: str = Field(..., default= PostType.Question, description="Type of the question post")
    
    title: str = Field(..., max_length=TableCharLimit.post_title, description="Title of the question post")
    body: str = Field(..., max_length=TableCharLimit.post_detail, description="Body of the question post")
    
    is_anonymous: bool
    is_drafted: bool
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int
    
    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Question:
            raise ValueError('type must be Q')

    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 3:
            raise ValueError('There can be up to 3 tags')
        for tag in v:
            # if isinstance(tag, str) and len(tag) > TableCharLimit.tag:
            #     raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
            if len(tag) > TableCharLimit.tag:
                raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
        return v

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