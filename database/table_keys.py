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
    _lang       = "members"
    _int_area   = "members"
    _mem_status = "status"
    _signin     = "session"
    _promo      = 'promo_offers'
    

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
    
    table_name  = "T_Signin_Session_Hist"
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
    
    py_table_name = "PromoOffer"
    _memb       = "member_profile"
    
    created_by_default = "system"
    