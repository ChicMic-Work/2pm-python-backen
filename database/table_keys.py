class BaseKey():
    
    ID          = "id"
    
    create_at   = "create_at"
    update_at   = "update_at"
    add_at      = "add_at"
    add_type    = "add_type"
    
    add_date    = "add_date"
    add_by      = "add_by"
    
    schema_mbr      = "mbr"
    schema_pst      = "pst"
    schema_clb      = "clb"
    
    @classmethod
    def column_with_tn(cls, key_nm: str) -> str:
        return f"{cls.table_name}.{key_nm}"




class MemberProfileKeys(BaseKey):
    
    table_name_curr    = "mbr_profile_curr"
    table_name_hist    = "mbr_profile_hist"
    
    
    
    id          = "mbr_id"
    apple_id    = "apple_id"
    google_id   = "google_id"
    join_at     = "mbr_join_at"
    
    alias       = "df_alias"
    alias_std   = "df_alias_std"
    
    bio         = "df_bio"
    image       = "df_img"
    gender      = "gender"
    is_dating   = "is_dating "
    
    mem_id_FK   = BaseKey.schema_mbr + "." + table_name_curr + "." + id

    gender_validation = ["Male", "Female", "Other"]
    is_dating_default = 0

    py_table_name = "MemberProfileCurr"
    
    _mem_bill_curr  = "mem_bill_curr"
    _mem_bill_prev  = "mem_bill_prev"
    
    _waiver         = "waivers"
    _promo          = "promos"
    
    _mem_lang   = "language_choices"
    _mem_int_area   = "interest_area_choices"
    
    _mem_status_curr = "status_curr"
    _mem_status_hist = "status_hist"
    
    _sign_in_curr     = "session_curr"
    _sign_in_prev     = "session_prev"
    
    _mem_foll_curr_fling = "mem_foll_curr_fling"
    _mem_foll_curr_flwed = "mem_foll_curr_flwed"
    
    _mem_foll_prev_fling = "mem_foll_prev_fling"
    _mem_foll_prev_flwed = "mem_foll_prev_flwed"
    
    _view_followers_count= "followers_count"
    
    _mem_curr_muted     = "mem_curr_muted"
    _mem_curr_muted_by  = "mem_curr_muted_by"
    
    _mem_prev_muted     = "mem_prev_muted"
    _mem_prev_muted_by  = "mem_prev_muted_by"
    
    _mem_curr_spam     = "mem_curr_spam"
    _mem_curr_spam_by  = "mem_curr_spam_by"
    
    _mem_prev_spam     = "mem_prev_spam"
    _mem_prev_spam_by  = "mem_prev_spam_by"
    
    _mem_ban_curr = "ban_curr"
    _mem_ban_prev = "ban_prev"
    
    _mem_curr_reported     = "mem_curr_reported"
    _mem_curr_reported_by  = "mem_curr_reported_by"
    
    _mem_posts         = "posts"
    _mem_draft_posts   = "draft_posts"
    
    _mem_comments      = "comments"
    
    _poll_taken        = "poll_taken"
    
    _daily_ans         = "daily_ans"
    
    _mem_tags          = "mem_tags"
    
    _mem_post_like_curr = "mem_post_like_curr"
    _mem_post_like_hist = "mem_post_like_hist"
    
    _mem_post_fav_curr  = "mem_post_fav_curr"
    _mem_post_fav_hist  = "mem_post_fav_hist"
    
    _mem_post_fol_curr  = "mem_post_fol_curr"
    _mem_post_fol_hist  = "mem_post_fol_hist"
    
    _mem_poll_post_inviting  = "poll_post_inviting"
    _mem_poll_post_invited   = "poll_post_invited"
    
    _mem_ques_post_inviting  = "ques_post_inviting"
    _mem_ques_post_invited   = "ques_post_invited"
    
    _mem_cmnt_like      = "mem_cmnt_like"
    
    _feedback           = "feedback"
    
    _post_share_by      = "post_share_by"
    _post_share_to      = "post_share_to"
    
    _promo              = "promo_offers"
    _fav_received       = "favorite_like_received"
    _post_invites       = "post_invites"
    _total_post_count   = "total_post_count"
    _mem_alias_hist     = "member_alias_hist"




class MmbLangKeys(BaseKey):
    
    table_name  = "mbr_language"
    
    id          = "id"
    member_id   = "mbr_id"
    language_id = "lang_id"
    
    py_table_name = "MemberLang"
    _memb         = "member_profile"
    
class MmbIntAreaKeys(BaseKey):
    
    table_name  = "mbr_topic_area"
    
    id          = "id"
    member_id   = "mbr_id"
    int_area_id = "topic_area_id"
    
    py_table_name = "MemberIA"
    
class LanguageKeys(BaseKey):
    
    table_name  = "language_choice"
    id          = "lang_id"
    name        = "lang_nm"
    
    lang_id_FK  = BaseKey.schema_clb+ "." + table_name + "." + id 
    
    py_table_name = "Languages"
    _memb       = "language_choices"
    _posts      = "posts"
    _draft_posts= "draft_posts"
    
class InterestAreaKeys(BaseKey):
    
    table_name  = "topic_area"
    id          = "topic_area_id"
    name        = "topic_area_nm"
    
    int_id_FK   = BaseKey.schema_clb+ "." + table_name + "." + id 
    
    py_table_name = "InterestAreas"
    _memb       = "interest_area_choices"
    _posts      = "posts"
    _draft_posts= "draft_posts"
    



class MbrStatusKeys(BaseKey):
    
    table_name_curr    = "mbr_status_curr"
    table_name_hist    = "mbr_status_hist"
    
    member_id   = "mbr_id"
    
    product_id  = "mbrshp_prod_id"
    product_fee = "mbrshp_prod_fee_amt"
    product_period = "mbrshp_prod_period"
    
    member_status = "mbr_status"
    is_banned   = "is_banned"
    
    
    is_banned_default = 0
    
    py_table_name = "MbrStatusCurr"
    py_table_name_hist = "MbrStatusHist"
    
    _memb         = "member_profile"


class SignInKeys(BaseKey):
    
    table_name_curr  = "mbr_session_curr"
    table_name_prev  = "mbr_session_prev"
    
    id          = "session id"
    member_id   = "mbr_id"
    signin_at   = "sign_in_at"
    signin_id   = "sign_in_id"
    type        = "sign_in_type"
    ip          = "sign_in_ip"
    device_type = "sign_in_device_type"
    device_model= "sign_in_device_model"
    signout_at  = "sign_out_at"
    
    py_table_name = "SessionCurr"
    py_table_name_prev = "SessionPrev"
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
    
