from pydantic import (
    BaseModel, field_validator, Field, AwareDatetime
)
from uuid import UUID

from utilities.constants import (
    PollPostLimit, PostType, TableCharLimit
)

from typing import List, Optional, Union

#BLOG
class PostBlogRequest(BaseModel):
    type: str = Field(default= PostType.Blog, description="Blog post")
    
    title: str = Field(..., description="Title of the blog post")
    body: str = Field(..., description="Body of the blog post")
    
    draft_id: Optional[UUID] = Field(None, description="Deletes the draft and posts blog")
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
    type: str = Field(default= PostType.Blog, description= "Blog Post")
    
    title: str = Field(None,  description="Title of the blog post")
    body: str  = Field(None, description="Body of the blog post")
    
    draft_id: Optional[UUID] = Field(None, description="Changes existing Drafted Blog Post")
    
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


#QUESTION
class PostQuesRequest(BaseModel):
    type: str = Field( default= PostType.Question, description="Question Post")
    
    title: str = Field(..., description="Title of the question post")
    body: str = Field(..., description="Body of the question post")
    
    draft_id: Optional[UUID] = Field(None, description="Deletes the draft and posts question")
    is_anonymous: bool
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int
    
    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Question:
            raise ValueError('type must be Q')
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

class PostQuesDraftRequest(BaseModel):
    type: str = Field( default= PostType.Question, description="Question Post")
    
    title: str = Field(None,  description="Title of the question post")
    body: str  = Field(None,  description="Body of the question post")
    
    draft_id: Optional[UUID] = Field(None, description="Changes existing Drafted Question Post")
    
    tags: Optional[List[Union[str, int]]] = []
    interest_area_id: int
    language_id: int

    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Question:
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


#RESPONSE - BLOG, QUESTION
class PostBlogQuesResponse(BaseModel):
    
    post_id: str
    member: dict
    
    type: str
    title: str
    body: str
    
    tags: Optional[List[Union[str, int]]] = []
    
    interest_area_id: int
    language_id: int

    post_at: AwareDatetime


class InvitedQuesResponse(BaseModel):

    post_id: str
    member: dict
    
    type: str
    title: str
    body: str

    post_at: AwareDatetime
    invited: dict



#ANSWER
class PostAnsRequest(BaseModel):
    type: str = Field(default= PostType.Answer, description="Answer Post")
    
    title: str = Field("Answer", description="Title of the answer post")
    body: str = Field(..., description="Body of the answer post")
    
    post_ques_id: UUID = Field(..., description="Question Post ID")

    draft_id: Optional[UUID] = Field(None, description="Deletes the draft and posts answer")
    is_anonymous: bool
    is_for_daily: bool = Field(False, description="is the answer for the daily question")
    
    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Answer:
            raise ValueError('type must be A')
        return v

class PostAnsDraftRequest(BaseModel):

    type: str = Field(default= PostType.Answer, description="Answer Post")

    title: str = Field("Answer",  description="Title of the answer post")
    body: str  = Field(...,  description="Body of the answer post")

    post_ques_id: UUID = Field(..., description="Question Post ID")
    
    draft_id: Optional[UUID] = Field(None, description="Changes existing Drafted Answer Post")
    is_for_daily: bool = Field(False, description="is the answer for the daily question")

    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Answer:
            raise ValueError('type must be A')
        return v



#RESPONSE - ANSWER
class PostAnsResponse(BaseModel):
    
    post_id: str | None
    member: dict | None
    
    type: str
    title: str
    body: str | None
    
    post_ques_id: str
    
    is_for_daily: bool

    post_at: AwareDatetime | None


#POLL
class PollQuesChoicesReqBase(BaseModel):
    
    poll_item_id: str   = Field("", description="Poll Item ID, Used in response")
    ans_seq_letter: str = Field(...,  description="Choice Sequence Letter")
    ans_text: str       = Field("",  description="Choice Text")
    
    percentage: int | None    = None
    selected_count: int | None = None

    @field_validator('ans_seq_letter')
    def validate_ans_seq_letter(cls, v):
        if v not in PollPostLimit.ans_seq_letter_list:
            raise ValueError(f'Choice Sequence Letter must be one of {PollPostLimit.ans_seq_letter_list}')
        return v

class PollQuesChoicesRequest(PollQuesChoicesReqBase):
    ans_text: str       = Field(..., description="Choice Text")


class PollQuesChoicesDraftRequest(PollQuesChoicesReqBase):
    ans_text: str       = Field("", description="Choice Text")





class PollQuestionReqBase(BaseModel):
    
    qstn_seq_num: int = Field(..., ge=PollPostLimit.qstn_seq_num_min, le=PollPostLimit.qstn_seq_num_max, description="Question Sequence Number")
    ques_text: str    = Field("",  description="Question Text")

    allow_multiple: bool
    

class PollQuestionRequest(PollQuestionReqBase):
    
    ques_text: str    = Field(..., description="Question Text")

    allow_multiple: bool

    choices: List[PollQuesChoicesRequest]

    @field_validator("choices")
    def validate_choices_length(cls, value):
        if len(value) > PollPostLimit.max_choices:
            raise ValueError("Maximum of 5 choices allowed per question")
        if len(value) < 2:
            raise ValueError("Poll must have at least 2 choices")
        return value
    
class PollQuestionDraftReq(PollQuestionReqBase):
    
    ques_text: str    = Field("", description="Question Text")

    allow_multiple: bool

    choices: List[PollQuesChoicesDraftRequest]

    @field_validator("choices")
    def validate_choices_length(cls, value):
        if len(value) > PollPostLimit.max_choices:
            raise ValueError("Maximum of 5 choices allowed per question")
        return value
    

class PostPollReqBase(BaseModel):
    type: str = Field( default= PostType.Poll, description="Poll Post")
    
    title : str = Field("",  description="Title of the poll post")
    body: str = Field("",  description="Body of the poll post")

    interest_area_id: int
    language_id: int
    
    @field_validator('type')
    def validate_type(cls, v):
        if v != PostType.Poll:
            raise ValueError('type must be P')
        return v
    

class PostPollRequest(PostPollReqBase):
    
    title: str = Field(..., description="Title of the poll post")

    draft_id: Optional[UUID] = Field(None, description="Deletes the draft and posts answer")
    is_anonymous: bool

    tags: Optional[List[Union[str, int]]] = []

    poll: List[PollQuestionRequest]
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 3:
            raise ValueError('There can be up to 3 tags')
        if len(v) == 0:
            raise ValueError('There must be at least 1 tag')
        for tag in v:
            if len(tag) > TableCharLimit.tag:
                raise ValueError(f'Tag "{tag}" exceeds the maximum length of {TableCharLimit.tag}')
        return v

    @field_validator("poll")
    def validate_poll_length(cls, value):
        if len(value) > PollPostLimit.max_qstns:
            raise ValueError("Maximum of 5 questions allowed per poll")
        if len(value) == 0:
            raise ValueError("Poll must have at least 1 question")
        
        return value

class PostPollDraftRequest(PostPollReqBase):


    draft_id: Optional[UUID] = Field(None, description="Deletes the draft and posts answer")

    interest_area_id: int
    language_id: int

    poll: List[PollQuestionDraftReq]

    @field_validator("poll")
    def validate_poll_length(cls, value):
        if len(value) > PollPostLimit.max_qstns:
            raise ValueError("Maximum of 5 questions allowed per poll")
        
        return value

#RESPONSE - POLL
class PostPollResponse(BaseModel):
    
    post_id: str
    member: dict
    
    type: str
    
    title: str
    body: str
    
    tags: Optional[List[Union[str, int]]] = []
    
    interest_area_id: int
    language_id: int

    poll: List[PollQuestionRequest]

    post_at: AwareDatetime

class PostPollDraftResponse(BaseModel):
    
    post_id: str
    member: dict
    
    type: str
    
    title: str = ""
    body: str = ""
    
    interest_area_id: int
    language_id: int

    poll: List[PollQuestionDraftReq]

    post_at: AwareDatetime





"""
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
        return type
    
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

"""