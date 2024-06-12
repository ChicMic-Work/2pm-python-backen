import pytz, os
from dotenv import load_dotenv

from datetime import datetime, timedelta
from sqlalchemy import func

load_dotenv()
SECRET_KEY  = os.getenv("SECRET_KEY")
ALGORITHM   = os.getenv("ALGORITHM")

EMAIL_HOST          = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT          = os.getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL")

APPLE_TOKEN_ISS     = os.getenv("APPLE_TOKEN_ISS")
APPLE_TOKEN_AUD     = os.getenv("APPLE_TOKEN_AUD")
APPLE_AUTH_KEY_URL  = os.getenv("APPLE_AUTH_KEY_URL")
GOOGLE_TOKEN_AUD    = os.getenv("GOOGLE_TOKEN_AUD")
GOOGLE_AUTH_KEY_URL = os.getenv("GOOGLE_AUTH_KEY_URL")

#S3
UPLOAD_TO_S3    = os.getenv("UPLOAD_TO_S3")
S3_BUCKET_NAME  = os.getenv("S3_BUCKET_NAME")
CLOUDFRONT_URL  = os.getenv("CLOUDFRONT_URL")
S3_REGION       = os.getenv("S3_REGION")
S3_ACCESS_KEY_ID        = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY    = os.getenv("S3_SECRET_ACCESS_KEY")

#Redis
REDIS_DB        = int(os.getenv("REDIS_DB"))

access_token_expire = timedelta(days=30)

AuthTokenHeaderKey = "Auth-Token"
protected_endpoints = [
    '/profile/create/', '/profile/alias', '/profile/image/', '/profile/user',
    '/profile/choices/', '/auth/logout/', '/profile/get/users/', '/profile/get/posts/users/',
    '/profile/follow/',
    '/posts/create/blog/', '/posts/create/question/', '/posts/create/poll/', '/posts/create/answer/',
    '/posts/draft/blog/', '/posts/draft/question/', '/posts/draft/poll/', '/posts/draft/answer/',
    '/posts/get/drafts/', '/posts/get/questions/', '/posts/get/polls/',
    '/posts/take/poll/', '/posts/reveal/poll/',
    '/posts/hop/', '/posts/cd/', '/posts/mp/', '/posts/search/', '/posts/pr/',
]

def current_datetime():
    return datetime.now(tz=pytz.utc)

class PollPostLimit:
    
    qstn_seq_num_min = 1
    qstn_seq_num_max = 5

    ans_seq_letter_len = 1
    ans_seq_letter_list = ['A', 'B', 'C', 'D', 'E']

    max_qstns    = 5
    max_choices  = 5

class AddType:

    Insert = 'I'
    Update = 'U'
    Add    = 'A'
    Delete = 'D'


class ContentType:
    
    daily_club_ans  = "A"
    post            = "P"
    comment         = "C"
    homepage        = "H"

class TableCharLimit:
    post_title  = 70
    post_detail = 5000
    alias       = 20
    bio         = 150
    comment     = 300
    tag         = 25
    feedback    = 1000

    poll_qstn   = 150
    poll_choice = 70
    
    _255        = 255
    _330        = 330


class PaginationLimit:

    random = 30
    most_popular = 30

class SocialType:
    Google = 0
    Apple = 1

    _0 = "Google"
    _1 = "Apple"
    
    
class ChoicesType:
    Interest_Area = 0
    Language = 1
    
    
class PromoType:
    T = "Free Trial"
    S = "Fee Waiver"
    M = "Manual"
    

class PostType:
    Blog = "B"
    Question = "Q"
    Answer = "A" 
    Poll = "P"
    
    types_list = ['B', 'Q', 'A', 'P']

PGROONGA_OPERATOR = 'OPERATOR(mbr.&@)'

ALIAS_VALID     = "Valid"
ALIAS_INVALID   = "Invalid"
ALIAS_EXISTS    = "Nickname is already in use"
ALIAS_CURRENT   = "Current"
ALIAS_INVALID_CHARACTER = "Your input contains an invalid character"
ALIAS_ATLEAST = "Nickname must contain at least one letter"
ALIAS_STARTS = "Nickname must start with a letter"
ALIAS_ATMOST = "Nickname must not exceed 20 characters"
BIO_ATMOST = "Bio must not exceed 150 characters"

IMAGE_FAIL = "Failed to save image"
USER_NOT_FOUND = "User not found"
USER_LOGGED_OUT = "User logged out"
SESSION_NOT_EXIST = "Session does not exist"
INVALID_SOCIAL_TOKEN = "Invalid Social Token"

POST_CREATED = "Post created"
DRAFT_CREATED = "Draft created"

DAILY_QUES_NOT_FOUND = "Daily question not found"
QUES_NOT_FOUND = "Question not found"
DRAFT_NOT_FOUND = "Draft not found"

INVALID_POST_TYPE = "Invalid post type"
INVALID_SEARCH_QUERY = "Invalid search query"
EMPTY_SEARCH_STRING = "Search string cannot be empty"
INVALID_SORT_TYPE = "Invalid sort_type. Must be 'newest' or 'random'."

DUPLICATE_POLL_ITEM_IDS = "Duplicate poll item ids"
POLL_ITEM_NOT_FOUND = "Poll item not found"
POST_NOT_FOUND = "Post not found"
POST_DELETED = "Post is deleted"
POST_BLOCKED = "Post is blocked"
INVALID_POLL_ITEM = "One or more poll items are invalid or do not belong to the specified post"
POLL_ALREADY_TAKEN = "User already took poll"
POLL_ALREADY_REVEALED = "User already revealed poll"

UNFOLLOWED = "Unfollowed"
FOLLOWED = "Followed"



class RandomSample:
    
    _10 = 10
    _5  = 5


class ResponseKeys:
    STATUS = "status"
    MESSAGE = "message"
    DATA = "data"
    DRAFT_ID = "draft_id"
    
class ResponseMsg:
    
    SUCCESS = "success"
    FAIL = "fail"
    ERROR = "error"
    CREATED = "created"

class PostListType:
    
    random = "random"
    popular = "popular"
    search = "search"
    invites = "invites"

class HOPSortType:
    
    newest = "newest"
    random = "random"

class RedisKeys:

    revoked_tokens = "revoked_tokens"
"""
TIMEZONE = 'Asia/Kolkata' pytz.timezone(TIMEZONE)
"""