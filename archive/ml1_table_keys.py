class BaseKey():
    created_at = "Created_At"
    updated_at = "Updated_At"
    
    @classmethod
    def column_with_tn(cls, key_nm: str) -> str:
        return f"{cls.table_name}.{key_nm}"


class MemberProfileKeys(BaseKey):
    
    table_name  = "Mbr_Profile_Hist"
    _table_name_curr    = "Mbr_Profile_Curr"
    _table_name_prev    = "Mbr_Profile_Prev"
    
    id          = "Mbr_ID"
    apple_id    = "Apple_ID"
    google_id   = "Google_ID"
    join_at     = "Mbr_Join_At"
    
    alias       = "DF_Nicknm"
    bio         = "DF_Bio"
    image       = "DF_Img"
    gender      = "Gender"
    is_dating   = "Is_Dating"
    
    add_at      = "Add_At"
    is_current  = "Is_Current"
    
    mem_id_FK   = table_name + "." + id

    gender_validation = ["Male", "Female", "Other"]
    is_dating_default = 0

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
    _mem_alias_hist     = "member_alias_hist"
    

class MmbLangKeys(BaseKey):
    
    table_name  = "Mbr_Language_Choice"
    id          = "ID"
    member_id   = "Mbr_ID"
    language_id = "Lang_ID"
    add_at      = "Add_At"
    
    
class MmbIntAreaKeys(BaseKey):
    
    table_name  = "Mbr_Interest_Area"
    id          = "ID"
    member_id   = "Mbr_ID"
    int_area_id = "Int_Area_ID"
    add_at      = "Add_At"
    

class LanguageKeys(BaseKey):
    
    table_name  = "Lang_Choice_List"
    id          = "Lang_ID"
    name        = "Lang_Nm"
    create_data = "Create_Date"
    
    lang_id_FK  = table_name + "." + id 
    
    py_table_name = "Languages"
    _memb       = "language_choices"
    

class InterestAreaKeys(BaseKey):
    
    table_name  = "Int_Area_List"
    id          = "Int_Area_ID"
    name        = "Int_Area_Nm"
    create_data = "Create_Date"
    
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

    prod_id         = "Membership_Product_ID"
    prod_start_time = "Membership_Product_Start_Datetime"
    prod_fee_amount = "Membership_Product_Fee_Amt"
    prod_period     = "Membership_Product_Period"
    
    memb_sub_level  = "Mbrshp_Lvl"
    memb_started_at = "Mbrshp_Started_At"
    memb_sub_status = "Mbrshp_Status"
    
    billing_id          = "Billing_Cycle_ID"
    billing_started_at  = "Billing_Cycle_Start_At"
    billing_end_at      = "Billing_Cycle_End_At"
    billing_charge_amount  = "Billing_Cycle_Charged_Amt"
    next_billing_charge_at = "Next_Billing_Cycle_Charged_At"
    
    is_current             = "Is_Current"
    
    cancelled_at= "Cancelled_At"

    memsub_id_FK= table_name +"." + id

    py_table_name = "MemSub"
    _memb         = "member_profile"
    _member_posts = "member_posts"


class PostKeys(BaseKey):

    table_name  = "T_Post"
    id          = "Promo_Offer_ID"
    member_id   = "Author_ID"
    mem_sub_id  = "Membership_Subscription_ID"
    intrst_id   = "Interest_Area_ID"
    lang_id     = "Language_ID"



    type        = "Type"
    # "Tag1"
    # "Tag2"
    # "Tag3"
    title       = "Title"
    body        = "Body"
    ass_post_id = "Assoc_Qstn_Post_ID"
    

    post_id_FK   = table_name + "." + id
    key_default = 0

    py_table_name = "Post"

    _memb               = "member_profile"
    _mem_sub            = "member_sub"
    _total_post_count   = "total_post_count"
    _parent_post        = "parent_post"
    _answers            = "associated_post"
    _post_stat          = "post_stat"


class PostStatKeys(BaseKey):
    
    table_name  = "T_Post_Stat"
    id          = "T_Post_Stat_ID"
    post_id     = "Post_ID"
    
    is_anonymous= "Is_Anonymous"
    is_blocked  = "Is_Blocked"
    
    view_count  = "View_Cnt"
    like_count  = "Like_Cnt"
    fav_count   = "Favorite_Cnt"
    ans_count   = "Answer_Cnt"
    following_count = "Following_Cnt"
    comment_count  = "Comment_Cnt"
    poll_entry_count = "Poll_Entry_Cnt"
    share_count = "Share_Cnt"
    report_count= "Report_Cnt"
    post_score  = "Post_Score"
    
    _post       = "post"



class PostQuesKeys(BaseKey):
    
    table_name  = "T_Poll_Questions"
    id          = "Question_ID"
    seq_num     = "Question_Seq_Num"
    ques_text   = "Question_Text"

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


class MemAliasHistKeys(BaseKey):
    
    table_name  = "T_Member_Discussion_Nickname_Hist"
    id          = "ID"
    member_id   = "Member_ID"
    alias       = "Discussion_Forum_Nickname"
    
    py_table_name = "MemAliasHist"
    
    _memb       = "member_profile"
    
    
class AliasHistKeys(BaseKey):
    
    table_name  = "T_Discussion_Nickname_Hist"
    id          = "ID"
    alias       = "Discussion_Forum_Nickname"
    
    py_table_name = "AliasHist"
    
