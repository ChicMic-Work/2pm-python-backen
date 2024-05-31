
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
 
class MmbBillCycleKeys(BaseKey):
    
    table_name_curr   = "mbr_bill_cycle_curr"
    table_name_prev   = "mbr_bill_cycle_prev"
    
    member_id       = "mbr_id"
    
    product_id      = "prod_id"
    product_fee     = "prod_fee_amt"
    product_period  = "prod_period"
    prod_start_at   = "prod_start_at"
    
    next_cycle_at   = "Next_Bill_Cycle_Charge_At"
    next_cycle_id   = "Next_Bill_Cycle_ID"
    
    bill_cycle_id   = "bill_cycle_id"
    bill_cycle_start_at     = "bill_cycle_start_at"
    bill_cycle_end_at       = "bill_cycle_end_at"
    bill_cycle_charge_amount= "bill_cycle_charge_amt"
    
    bill_cycle_blog_count   = "bill_cycle_blog_cnt"
    bill_cycle_ques_count   = "bill_cycle_question_cnt"
    bill_cycle_ans_count    = "bill_cycle_answer_cnt"
    bill_cycle_poll_count   = "bill_cycle_poll_cnt"
    bill_cycle_poll_taken_count = "bill_cycle_poll_taken_cnt"
    
    bill_cycle_actvy_count  = "bill_cycle_actvy_cnt"
    
    default_count   = 0
    
    py_table_name   = "MmbBillCycleCurr"
    py_table_name_prev   = "MmbBillCyclePrev"
    
    _memb       = "member_profile"

class MmbWaiverKeys(BaseKey):
    
    tablename   = "mbr_bill_cycle_waiver_calc_hist"
    
    member_id       = "mbr_id"
    bill_cycle_id   = "bill_cycle_id"
    
    calculated_at   = "waiver_calc_at"
    
    blog_count      = "prev_bill_cycle_qual_blog_cnt"
    quest_count     = "prev_bill_cycle_qual_qstn_cnt"
    ans_count       = "prev_bill_cycle_qual_answer_cnt"
    poll_count      = "prev_bill_cycle_qual_poll_cnt"
    poll_taken_count= "prev_bill_cycle_qual_poll_taken_cnt"
    activity_count  = "prev_bill_cycle_qual_act_cnt"
    is_eligible     = "is_waiver_eligible"
    
    py_table_name   = "MmbWaiver"
    _memb       = "member_profile"
    
class PromoOfferKeys(BaseKey):
    
    tablename   = "mbr_promo_offer_hist"
    
    offer_id    = "offer_id"
    member_id   = "mbr_id"
    bill_cycle_id   = "bill_cycle_id"
    
    type        = "offer_type"
    disc_applied= "discnt_amt_or_pct"
    
    assc_product= "assoc_prod"
    
    offer_start_at  = "offer_start_at"
    offer_end_at  = "offer_end_at"
    
    status  = "redeem_status"
    redeemed_at = "redeem_at"
    
    create_by   = "create_by"
    
    py_table_name = "PromoOffer"
    
    _memb       = "member_profile"
    
    default_create_by = "Admin"



        
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
    
class MmbFollowKeys(BaseKey):
    
    table_name_curr = "mbr_follow_curr"
    table_name_prev = "mbr_follow_hist"
    
    following_id    = "following_mbr_id"
    followed_id     = "followed_mbr_id"
    follow_at       = "follow_at"
    
    py_table_name   = "MmbFollowCurr"
    py_table_name_prev = "MmbFollowHist"
    
    _following_member = "following_member"
    _followed_member  = "followed_member"

class ViewMemFollKeys(BaseKey):
    
    table_name = "v_mbr_follow_cnt"
    
    member_id   = "Mbr_ID"
    following   = "following_cnt"
    follower    = "follower_cnt"
    
    py_table_name = "ViewMemFollowers" 
    
    _memb = "member_profile"




class PostKeys(BaseKey):

    table_name  = "post_posted"
    
    id          = "post_id"
    member_id   = "mbr_id"
    
    type        = "post_type"
    
    interest_id = "topic_area_id"
    lang_id     = "lang_id"

    tag1        = "tag1"
    tag2        = "tag2"
    tag3        = "tag3"
    
    tag1_std    = "tag1_std"
    tag2_std    = "tag2_std"
    tag3_std    = "tag3_std"
    
    title       = "post_title"
    body        = "post_detail"
    
    assc_post_id= "assoc_qstn_post_id"
    
    posted_at   = "post_at"

    post_id_FK  = BaseKey.schema_pst + "." + table_name + "." + id

    py_table_name = "Post"

    _memb               = "member_profile"
    _answers            = "associated_post"
    _interest_area      = "interest_area"
    _language           = "language"
    
    _post_curr_status   = "post_curr_status"
    _post_prev_status   = "post_prev_status"
    
    _post_curr_block    = "post_curr_block"
    _post_prev_block    = "post_prev_block"
    
    _post_views         = "post_views"
    _post_view_count    = "post_view_count"
    
    _post_comments      = "comments"
    
    _poll               = "poll_ques"
    _poll_result        = "poll_result"
    _poll_mem_result    = "poll_mem_result"
    
    _post_score         = "post_score"
    
    _mem_post_like_curr = "mem_post_like_curr"
    _mem_post_like_hist = "mem_post_like_hist"
    
    _mem_post_fav_curr  = "mem_post_fav_curr"
    _mem_post_fav_hist  = "mem_post_fav_hist"

    _mem_post_fol_curr  = "mem_post_fol_curr"
    _mem_post_fol_hist  = "mem_post_fol_hist"
    
    _poll_invite        = "poll_invite"
    
    _ques_invite        = "ques_invite"
    _ques_invite_ans    = "ques_invite_ans"
    
    _post_share         = "post_share"

class PostDraftKeys(BaseKey):
    
    table_name = "post_draft"
    
    id      = "draft_id"
    
    member_id   = "mbr_id"
    
    type        = "post_type"

    interest_id = "topic_area_id"
    lang_id     = "language_id"
    
    is_for_daily= "is_4daily"
    
    title       = "post_title"
    body        = "post_detail"

    assc_post_id= "assoc_qstn_post_id"
    
    save_at     = "save_at"
    
    post_draft_id_FK   = BaseKey.schema_pst + "." + table_name + "." + id
    
    py_table_name = "PostDraft"

    _memb               = "member_profile"
    _answers            = "associated_post"
    _interest_area      = "interest_area"
    _language           = "language"
    
class ViewPostScoreKeys(BaseKey):
    
    tablename   = "v_post_score"
    
    post_id     = "post_id"
    
    view_count  = "view_cnt"
    comment_cnt = "comment_cnt"
    like_cnt    = "like_cnt"
    favorite_cnt= "favorite_cnt"
    follow_cnt  = "follow_cnt"
    
    answer_cnt  = "answer_cnt"
    poll_entry_cnt  = "poll_entry_cnt"
    share_cnt  = "share_cnt"
    report_cnt  = "report_cnt"
    
    post_score  = "post_score"
    
    
    py_table_name   = "ViewPostScore"
    
    _post       = "post"
    
class PostLikeKeys(BaseKey):
    
    table_name_curr  = "post_like_curr"
    table_name_hist  = "post_like_hist"
    
    post_id     = "post_id"
    member_id   = "mbr_id"
    
    like_at     = "like_at"
    
    py_table_name   = "PostLikeCurr"
    py_table_name_hist  = "PostLikeHist"
    
    _post       = "post"
    _memb       = "member_profile"

class PostFavKeys(BaseKey):
    
    table_name_curr  = "post_fav_curr"
    table_name_hist  = "post_fav_hist"
    
    post_id     = "post_id"
    member_id   = "mbr_id"
    
    fav_at      = "fav_at"
    
    py_table_name   = "PostFavCurr"
    py_table_name_hist  = "PostFavHist"
    
    _post       = "post"
    _memb       = "member_profile"
    
class PostFolKeys(BaseKey):
    
    table_name_curr  = "post_follow_curr"
    table_name_hist  = "post_follow_hist"
    
    post_id     = "post_id"
    member_id   = "mbr_id"
    
    follow_at      = "follow_at"
    
    py_table_name   = "PostFolCurr"
    py_table_name_hist  = "PostFolHist"
    
    _post       = "post"
    _memb       = "member_profile"
    
class TagListKeys(BaseKey):
    
    tablename   = "discuss_forum_tag"
    
    name        = "df_tag_std"
    
    add_date    = "add_dt"
    
    py_table_name   = "TagList"

class ViewMmbTagKeys(BaseKey):
    
    tablename   = "v_mbr_tag_cnt"
    
    tag_std     = "df_tag_std"
    member_id   = "mbr_id"
    count       = "tag_cnt"
    
    _memb       = "member_profile"
    
    py_table_name   = "ViewMmbTag"




class PostViewCntKeys(BaseKey):
    
    tablename   = "post_view_cnt"
    
    post_id         = "post_id"
    count           = "view_cnt"
    
    py_table_name   = "PostViewCount"
    
    _post           = "post"
    
    count_default   = 0

class PostViewKeys(BaseKey):
    
    tablename   = "post_views"
    
    post_id         = "post_id"
    view_at         = "view_at"
    
    py_table_name   = "PostViews"
    
    _post           = "post"




class PostBlockKeys(BaseKey):
    
    table_name_curr  = "post_block_curr"
    table_name_hist  = "post_block_hist"
    
    post_id         = "post_id"
    
    note            = "note"
    
    add_by          = "add_by"
    
    block_by        = "block_by"
    block_at          = "block_at"

    py_table_name   = "PostBlockCurr"
    py_table_name_prev = "PostBlockHist"
    
    _post           = "post"
    _admin          = "admin"
    
    
    block_by_default   = "Admin"

class PostStatusKeys(BaseKey):
    
    table_name_curr = "post_status_curr"
    table_name_hist = "post_status_hist"
    
    post_id         = "post_id"
    
    is_anonymous    = "is_anonymous"
    is_deleted      = "is_deleted"
    
    is_blocked      = "is_blocked"
    
    default_key     = 0
    
    py_table_name   = "PostStatusCurr"
    py_table_name_prev   = "PostStatusHist"
    
    _post           = "post"




class CommentNodeKeys(BaseKey):
    
    tablename   = "post_comment_node"
    
    comment_id  = "comment_id"
    member_id   = "mbr_id"
    post_id     = "post_id"
    root_id     = "root_id"
    
    text        = "comment_text"
    is_deleted  = "is_deleted"
    
    py_table_name   = "CommentNode"
    
    _memb       = "member_profile"
    _post       = "post"
    
    _parent_of  = "parent_of"
    _child_of   = "child_of"
    
    _cmnt_like  = "cmnt_like"
    
    _total_likes= "total_likes"
    
    cmnt_fk_id  = BaseKey.schema_pst + "." + tablename+"."+comment_id

class CommentTreeKeys(BaseKey):
    
    tablename   = "post_comment_tree"
    
    parent_id   = "parent_id"
    child_id    = "child_id"
    root_id     = "root_id"
    depth       = "depth"
    
    py_table_name   = "CommentTree"
    
    _parent     = "parent_comment"
    _child      = "child_comment"
    
class CommentLikeKeys(BaseKey):
    
    tablename   = "mbr_comment_like"
    
    comment_id  = "comment_id"
    member_id   = "mbr_id"
    
    like_at     = "like_at"
    
    py_table_name   = "CommentLike"
    
    _comment    = "comment"
    _memb       = "member_profile"

class ViewCmntLikeCntKeys(BaseKey):
    
    tablename   = "v_post_comment_like_cnt"
    
    comment_id  = "comment_id"
    count       = "like_cnt"
    
    _comment    = "comment"
    
    py_table_name   = "ViewCommentLikeCount"

class PollQuesKeys(BaseKey):
    
    table_name  = "poll_detail"
    
    poll_item_id    = "poll_item_id"
    
    post_id         = "poll_post_id"
    ques_seq_id     = "qstn_seq_id"
    ques_text       = "qstn_text"
    
    ans_seq_id      = "answer_choice_seq_id"
    ans_text        = "answer_choice_text"

    _post           = "post"
    _poll_taken     = "poll_taken"
    _poll_result    = "poll_result"
    
    py_table_name   = "PollQues"
    
    poll_id_fk      = BaseKey.schema_pst + "." + table_name + "." + poll_item_id

class PollMemResultKeys(BaseKey):
    
    tablename   = "mbr_poll_result"
    
    poll_item_id    = "poll_item_id"
    post_id     = "poll_post_id"
    member_id   = "mbr_id"
    
    ques_seq_id = "qstn_seq_id"
    selected_id = "sel_answer_choice_seq_id"
    
    taken_at    = "taken_at"
    
    py_table_name   = "PollMemResult"
    
    _post           = "post"
    _memb           = "member_profile"
    _poll           = "poll"
        
class PollResultKeys(BaseKey):
    
    tablename   = "v_poll_result"

    poll_item_id    = "poll_item_id"
    
    post_id     = "poll_post_id"
    ques_seq_id = "qstn_seq_id"
    ans_seq_id  = "answer_choice_seq_id"
    count       = "select_cnt"
    
    py_table_name   = "PollResult"
    
    _post           = "post"
    _poll           = "poll"
    
class PollInvKeys(BaseKey):
    
    tablename   = "poll_invite"
    
    poll_post_id    = "poll_post_id"
    
    inviting_mbr_id = "inviting_mbr_id"
    invited_mbr_id  = "invited_mbr_id"
    
    invite_at       = "invite_at"
    
    py_table_name   = "PollInvite"
    
    _post           = "post"
    _inviting_member    = "inviting_member"
    _invited_member     = "invited_member"

class QuesInvKeys(BaseKey):
    
    tablename   = "question_invite"
    
    ques_post_id    = "qstn_post_id"
    ans_post_id     = "answer_post_id"
    
    inviting_mbr_id = "inviting_mbr_id"
    invited_mbr_id  = "invited_mbr_id"
    
    invite_at       = "invite_at"
    
    py_table_name   = "PollInvite"
    
    _post           = "post"
    _post_ans           = "post_ans"
    _inviting_member    = "inviting_member"
    _invited_member     = "invited_member"




class DailyQuesKeys(BaseKey):
    
    tablename   = "daily_qstn"
    
    id          = "daily_qstn_id"
    
    title       = "daily_qstn_title"
    is_live     = "is_live"
    
    add_dt      = "add_dt"
    update_dt   = "update_dt"
    
    py_table_name   = "DailyQues"
    
    _answer     = "answers"
    _post_score = "post_score"
    
    ques_fk_id  = f"{BaseKey.schema_pst}.{tablename}.{id}"
 
class DailyAnsKeys(BaseKey):
    
    tablename   = "daily_answer_posted"
    
    id          = "daily_answer_id"
    ques_id     = "assoc_daily_qstn_id"
    member_id   = "mbr_id"
    
    is_anonymous    = "is_anonymous"
    is_deleted      = "is_deleted"
    is_blocked      = "is_blocked"
    
    answer          = "post_detail"
    post_at         = "post_at"
    
    block_by        = "block_by"
    block_note      = "block_note"
    
    py_table_name   = "DailyAns"
    
    _ques           = "ques"
    _memb           = "member_profile"
 
class ViewDailyPostScoreKeys(BaseKey):
    
    tablename   = "v_daily_answer_score"
    
    answer_id     = "daily_answer_id"
    
    view_count  = "view_cnt"
    comment_cnt = "comment_cnt"
    like_cnt    = "like_cnt"
    favorite_cnt= "favorite_cnt"
    share_cnt  = "share_cnt"
    report_cnt  = "report_cnt"
    
    post_score  = "post_score"
    
    py_table_name   = "ViewDailyPostScore"  
    
    _daily_post = "daily_post"
    
  
    
    
class AliasHistKeys(BaseKey):
    
    table_name  = "discuss_forum_alias"

    alias       = "df_alias_std"
    
    py_table_name = "AliasHist"
   
class ClubAdminKeys(BaseKey):
    
    tablename   = "clb_admin"
    
    admin_id    = "admin_id"
    first_name  = "fst_name"
    last_name   = "lst_name"
    
    start_dt    = "start_dt"
    
    adm_id_fk   = BaseKey.schema_clb+"."+tablename+"."+admin_id
   
    py_table_name   = "ClubAdmin"
    
    _feedback   = "feedback"
    
    _mem_ban_curr    = "mem_ban_curr"
    _mem_ban_hist    = "mem_ban_hist"
    
    _post_block_curr = "post_block_curr"
    _post_block_hist = "post_block_hist"
    
    
class FeedbackKeys(BaseKey):
    
    tablename   = "feedback_log"
    
    feedback_id = "feedback_id"
    
    member_id   = "mbr_id"
    note_by     = "note_by"
    
    detail = "feedback_detail"
    email  = "contact_email"
    
    note    = "note"
    is_resolved = "is_resolved"
    
    feedback_at = "feedback_at"
    note_at = "note_at" 
    
    
    py_table_name   = "FeedbackLog"
    
    _memb   = "member_profile"
    _admin  = "admin"
    



class PostShareKeys(BaseKey):
    
    tablename   = "post_share"
    
    post_id     = "post_id"
    share_mbr_id    = "share_mbr_id"
    
    share_at    = "share_at"
    shared_to_type  = "shared_to_type"
    
    shared_to_id    = "shared_to_id"
    
    py_table_name   = "PostShare"
    
    _shared_by  = "shared_by"
    _shared_to  = "shared_to"
    _post   = "post"
    
    
    
    

# MUTE, SPAM, REPORT, BAN
class MmbMuteKeys(BaseKey):
    
    table_name_curr  = "mbr_mute_curr"
    table_name_hist  = "mbr_mute_hist"
    
    member_id        = "mbr_id"
    muted_mem_id     = "muted_mbr_id"

    py_table_name      = "MmbMuteCurr"
    py_table_name_prev = "MmbMuteHist"
    
    _muted_member    = "muted_member"
    _muted_by_member = "muted_by_member"
       
class MmbSpamKeys(BaseKey):
    
    table_name_curr  = "mbr_spam_curr"
    table_name_hist  = "mbr_spam_hist"
    
    member_id        = "mbr_id"
    spam_mem_id     = "spam_mbr_id"
    spam_at          = "spam_at"

    py_table_name = "MmbSpamCurr"
    py_table_name_prev = "MmbSpamHist"
    
    _spam_member    = "spam_member"
    _spam_by_member = "spam_by_member"
       
class MmbReportKeys(BaseKey):
    
    table_name  = "mbr_report_hist"
    
    reporting_id    = "reporting_mbr_id"
    reported_id     = "reported_mbr_id"
    
    content_type    = "content_type"
    content_id      = "content_id"
    
    is_daily        = "is_answer_4daily"
    
    reason_code     = "report_reason_code"
    reason_other_text = "report_others_reason_text"
    
    report_at       = "report_at"
    
    py_table_name   = "MmbReportHist"
    
    _reported_member    = "reported_member"
    _reported_by_member = "reported_by_member"
    
    _content        = "content"
    
    is_daily_default = 0
     
class MmbBanKeys(BaseKey):
    
    table_name_curr  = "mbr_ban_curr"
    table_name_hist  = "mbr_ban_hist"
    
    member_id        = "mbr_id"
    ban_by           = "ban_by"
    
    note             = "note"
    ban_at           = "ban_at"
    
    py_table_name    = "MmbBanCurr"
    py_table_name_prev = "MmbBanHist"
    
    _memb    = "member_profile"
    _admin   = "admin"
    
    ban_by_default   = "Admin"

class ReprResKeys(BaseKey):

    tablename   = "report_reason_type"
    
    type   = "report_reason_type"
    desc   = "report_reason_type_desc"




