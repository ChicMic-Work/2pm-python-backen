class BaseKey():
    created_at = "Created_At"
    updated_at = "Updated_At"
    
    @classmethod
    def column_with_tn(cls, key_nm: str) -> str:
        return f"{cls.table_name}.{key_nm}"


class MemberProfileKeys(BaseKey):
    
    table_name  = "T_Member_Profile"
    id          = "Member_ID"
    apple_id    = "Apple_ID"
    google_id   = "Google_ID"
    alias       = "Discussion_Forum_Alias"
    bio         = "Discussion_Forum_Bio"
    image       = "Discussion_Forum_Image"
    gender      = "Gender"
    created_at  = "Joined_At"
    updated_at  = "Updated_At"
    mem_id_FK   = table_name + "." + id

    gender_validation = ["Male", "Female", "Other"]

    py_table_name = "MemberProfile"
    _member_posts = "member_posts"
    _mem_sub    = "member_sub"
    _lang       = "members"
    _int_area   = "members"
    _mem_status = "status"
    _signin     = "session"
    _promo      = "promo_offers"
    _fav_received       = "favorite_like_received"
    _post_invites       = "post_invites"
    _total_post_count   = "total_post_count"
    

class MmbLangKeys(BaseKey):
    
    table_name  = "T_Member_Language_Choices"
    id          = "ID"
    member_id   = "Member_ID"
    language_id = "Language_ID"
    
    
class MmbIntAreaKeys(BaseKey):
    
    table_name  = "T_Member_Interest_Area_Choices"
    id          = "ID"
    member_id   = "Member_ID"
    int_area_id = "Interest_Area_ID"
    

class LanguageKeys(BaseKey):
    
    table_name  = "T_Language"
    id          = "Language_ID"
    name        = "Language_Name"
    lang_id_FK  = table_name + "." + id 
    
    py_table_name = "Languages"
    _memb       = "language_choices"
    

class InterestAreaKeys(BaseKey):
    
    table_name  = "T_Interest_Area"
    id          = "Interest_Area_ID"
    name        = "Interest_Area_Name"
    int_id_FK   = table_name + "." + id 
    
    py_table_name = "InterestAreas"
    _memb       = "interest_area_choices"
    
    
class MemberStatusKeys(BaseKey):
    
    table_name  = "T_Member_Status"
    id          = "Member_Status_ID"
    member_id   = "Member_ID"
    status      = "Status"
    deleted_at  = "Deleted_At"
    banned_at   = "Banned_At"
    report_count= "Report_Count"
    is_dating   = "Is_Dating"
    
    status_default = 2
    is_dating_default = 0
    report_count_default = 0
    validate_status = (1,2,3,4)
    
    py_table_name = "MemberStatus"
    _memb         = "member_profile"
    
    
class SignInKeys(BaseKey):
    
    table_name  = "T_Signin_Session_Hist"
    id          = "Signin_Session_Hist_ID"
    member_id   = "Member_ID"
    signin_at   = "Signin_At"
    signin_id   = "Signin_ID"
    type        = "Signin_Type"
    ip          = "Signin_IP"
    device_type = "Signin_Device_Type"
    device_model= "Signin_Device_Model"
    signout_at  = "Signout_At"
    
    py_table_name = "SignInSession"
    _memb       = "member_profile"
    
    
class PromoOfferKeys(BaseKey):
    
    table_name  = "T_Promo_Offer"
    id          = "Promo_Offer_ID"
    member_id   = "Member_ID"
    type        = "Type"
    code        = "Code"
    amount      = "Amount"
    # "Created_At"
    effective_at= "Effective_At"
    expires_at  = "Expires_At"
    redeemed_at = "Redeemed_At"
    created_by  = "Created_By"
    
    promo_id_FK = f"{table_name}.{id}"

    py_table_name = "PromoOffer"
    _memb         = "member_profile"
    _mem_sub      = "member_sub"
    
    created_by_default = "system"
    

class MemSubKeys(BaseKey):
    
    table_name  = "T_Member_Subscription"
    id          = "Member_Subscription_ID"
    member_id   = "Member_ID"
    promo_id    = "Promo_ID"

    memb_sub_level  = "Mbrshp_Lvl"
    memb_sub_status= "Mbrshp_Status"
    memb_sub_fee= "Mbrshp_Fee_Amt"
    
    started_at  = "Started_At"
    cancelled_at= "Cancelled_At"
    expired_at  = "Expired_At"

    memsub_id_FK= table_name +"." + id

    py_table_name = "MemSub"
    _memb         = "member_profile"
    _member_posts = "member_posts"
    _promo        = "promo_offer"


class PostKeys(BaseKey):

    table_name  = "T_Post"
    id          = "Promo_Offer_ID"
    member_id   = "Author_ID"
    mem_sub_id  = "Membership_Subscription_ID"
    intrst_id   = "Interest_Area_ID"
    lang_id     = "Language_ID"

    is_anonymous= "Is_Anonymous"
    is_drafted  = "Is_Drafted"

    type        = "Type"
    # "Tag1"
    # "Tag2"
    # "Tag3"
    title       = "Title"
    body        = "Body"
    ass_post_id = "Assoc_Qstn_Post_ID"
    is_blocked  = "Is_Blocked"

    post_id_FK   = table_name + "." + id
    key_default = 0

    py_table_name = "Post"

    _memb               = "member_profile"
    _mem_sub            = "member_sub"
    _total_post_count   = "total_post_count"
    _parent_post        = "parent_post"
    _associated_post     = "associated_post"


class MemFavRecKeys(BaseKey):

    table_name  = "T_Member_Favorite_Like_Received_Cnt"
    id          = "ID"
    member_id   = "Member_ID"
    fav_received = "Favorite_Received_Cnt"
    like_received= "Like_Received_Cnt"

    py_table_name = "MemFavReceived"
    _memb       = "member_profile"

    key_default = 0


class MemTotalPostKeys(BaseKey):

    table_name  = "T_Member_Post_Cnt"
    id          = "ID"
    member_id   = "Member_ID"

    post_count  = "Post_Cnt"
    blog_count  = "Blog_Cnt"
    question_count  = "Question_Cnt"
    answer_count    = "Answer_Cnt"
    poll_count      = "Poll_Cnt"

    taken_poll_count= "Taken_Poll_Cnt"
    
    draft_post_count= "Draft_Post_Cnt"
    draft_blog_count= "Draft_Blog_Cnt"
    draft_ques_count= "Draft_Question_Cnt"
    draft_ans_count = "Draft_Answer_Cnt"
    draft_poll_count= "Draft_Poll_Cnt"

    last_post_id    = "Last_Post_ID"
    last_post_lang  = "Last_Post_Written_Language_ID" #text
    last_post_interest = "Last_Post_Interest_Area_ID" #text

    py_table_name = "MemTotalPostCount"
    _memb       = "member_profile"

    key_default = 0
    _post       = "member_post"


class MemInvitesKeys(BaseKey):

    table_name  = "T_Member_Invite_Cnt"
    id          = "ID"
    member_id   = "Member_ID"
    ques_invites = "Invite_Question_Received_Cnt"
    poll_invites = "Invite_Poll_Received_Cnt"
    ques_invited = "Invite_Question_Sent_Cnt"
    poll_invited = "Invite_Poll_Sent_Cnt"

    py_table_name = "MemInvites"
    _memb       = "member_profile"

    key_default = 0



"T_Followers"
