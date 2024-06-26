
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, backref

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from datetime import datetime, timezone
import pytz
from pydantic import EmailStr

from utilities.constants import TableCharLimit

current_time = datetime.now(pytz.utc) 

from sqlalchemy import (
    Boolean, Column, Integer, String, SmallInteger, 
    DateTime, UUID, text, LargeBinary,
    ForeignKey, Table, func, PrimaryKeyConstraint,
    CheckConstraint, Index, Numeric,
    DDL, event, Date, Float, Text, BigInteger
    )

from database.table_keys import (
    ClubAdminKeys, CommentLikeKeys, CommentNodeKeys, CommentTreeKeys, DailyAnsKeys, DailyAnsLikeKeys, DailyAnsShareKeys, DailyCmntLikeKeys, DailyCommentNodeKeys, DailyCommentTreeKeys, DailyQuesKeys, FeedbackKeys, MemberProfileKeys, MmbBanKeys, MmbBillCycleKeys, MmbLangKeys,
    LanguageKeys, MmbIntAreaKeys,
    InterestAreaKeys, MmbMsgReportKeys, MmbMuteKeys, MmbReportKeys, MmbSpamKeys, MmbWaiverKeys, PollInvKeys, PollQuesKeys, PollMemResultKeys, PollResultKeys, PostBlockKeys, PostDraftKeys, PostFavKeys, PostFolKeys, PostLikeKeys, PostShareKeys, PostStatusKeys, PostViewCntKeys, PostViewKeys, QuesInvKeys, ReprResKeys,
    SignInKeys, PromoOfferKeys, PostKeys,
    AliasHistKeys, MmbFollowKeys,
    MbrStatusKeys, TagListKeys, ViewCmntLikeCntKeys, ViewDailyPostScoreKeys, ViewMemFollKeys, ViewMmbTagKeys, ViewPostScoreKeys
)

from sqlalchemy.orm import validates, relationship

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:1234@postgres:5432/2pm_ML1"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@postgres:5432/2pm_ML1"

#local local
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/2pm_test_sch"
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/2pm_test_sch"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL,)
# engine = create_engine(SQLALCHEMY_DATABASE_URL,)


SessionLocal = async_sessionmaker(bind= engine, autocommit=False, autoflush=False, class_= AsyncSession )
# SessionLocal = sessionmaker(bind= engine, autocommit=False, autoflush=False)

Base = declarative_base()

default_uuid7 = text("uuid_generate_v7()")
# default_uuid7 = text("uuid_generate_v4()")

class MemberProfileCurr(Base):
    
    __tablename__   = MemberProfileKeys.table_name_curr
    __table_args__ = {'schema': MemberProfileKeys.schema_mbr}
    
    id              = Column(MemberProfileKeys.id , UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    apple_id        = Column(MemberProfileKeys.apple_id, String(TableCharLimit._255), unique=True, index=True, nullable= True)
    apple_email     = Column(MemberProfileKeys.apple_email, String(TableCharLimit._255), nullable= True)
    google_id       = Column(MemberProfileKeys.google_id, String(TableCharLimit._255), unique=True, index=True)
    google_email    = Column(MemberProfileKeys.google_email, String(TableCharLimit._255), nullable= True)
    join_at         = Column(MemberProfileKeys.join_at, DateTime(timezone= True), default= func.now(), nullable= False)
    
    alias           = Column(MemberProfileKeys.alias, String(TableCharLimit._255), unique=True, index=True, nullable= True)
    alias_std       = Column(MemberProfileKeys.alias_std, String(TableCharLimit._255), unique=True, index=True, nullable= True)
    
    bio             = Column(MemberProfileKeys.bio, String(TableCharLimit._255), nullable= True)
    image           = Column(MemberProfileKeys.image, String(TableCharLimit._255), nullable= True)
    gender          = Column(MemberProfileKeys.gender, String(TableCharLimit._255), nullable= True)
    is_dating       = Column(MemberProfileKeys.is_dating, Boolean, default=MemberProfileKeys.is_dating_default, nullable= True)
    
    update_at       = Column(MemberProfileKeys.update_at, DateTime(timezone= True), nullable= True)
    
Index('ix_apple_id_curr_unique', MemberProfileCurr.apple_id, unique=True, postgresql_where=MemberProfileCurr.apple_id.isnot(None))
Index('ix_alias_curr_unique', MemberProfileCurr.alias, unique=True, postgresql_where=MemberProfileCurr.alias.isnot(None))
Index('ix_google_id_curr_unique', MemberProfileCurr.google_id, unique=True, postgresql_where=MemberProfileCurr.google_id.isnot(None))




class MmbBillCycleCurr(Base):
    
    __tablename__   = MmbBillCycleKeys.table_name_curr
    __table_args__  = {'schema': MmbBillCycleKeys.schema_mbr}
    
    member_id      = Column(MmbBillCycleKeys.member_id, UUID(as_uuid=True), primary_key= True, nullable= False)
    
    product_id      = Column(MmbBillCycleKeys.product_id, String(TableCharLimit._255))
    product_fee     = Column(MmbBillCycleKeys.product_fee, Numeric(10, 2))
    product_period  = Column(MmbBillCycleKeys.product_period, String(TableCharLimit._255))
    product_currency= Column(MmbBillCycleKeys.product_currency, String(TableCharLimit._255))
    prod_start_at   = Column(MmbBillCycleKeys.prod_start_at, DateTime(True))
    
    bill_cycle_id   = Column(MmbBillCycleKeys.bill_cycle_id, String(TableCharLimit._255), unique= True)
    bill_cycle_start_at     = Column(MmbBillCycleKeys.bill_cycle_start_at, DateTime(True))
    bill_cycle_end_at       = Column(MmbBillCycleKeys.bill_cycle_end_at, DateTime(True))
    bill_cycle_charge_amount= Column(MmbBillCycleKeys.bill_cycle_charge_amount, Numeric(10, 2))
    bill_cycle_charge_currency= Column(MmbBillCycleKeys.bill_cycle_charge_currency, String(TableCharLimit._255))
    
    bill_cycle_blog_count   = Column(MmbBillCycleKeys.bill_cycle_blog_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_ques_count   = Column(MmbBillCycleKeys.bill_cycle_ques_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_ans_count    = Column(MmbBillCycleKeys.bill_cycle_ans_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_poll_count   = Column(MmbBillCycleKeys.bill_cycle_poll_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_poll_taken_count   = Column(MmbBillCycleKeys.bill_cycle_poll_taken_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_actvy_count  = Column(MmbBillCycleKeys.bill_cycle_actvy_count, Integer, default= MmbBillCycleKeys.default_count)
    
    update_at               = Column(MmbBillCycleKeys.update_at, DateTime(True), nullable= True)

    
class MmbBillCyclePrev(Base):
    
    __tablename__   = MmbBillCycleKeys.table_name_prev
    __table_args__  = {'schema': MmbBillCycleKeys.schema_mbr}
    
    id             = Column(MmbBillCycleKeys.ID, BigInteger, primary_key= True)
    member_id      = Column(MmbBillCycleKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    product_id      = Column(MmbBillCycleKeys.product_id, String(TableCharLimit._255))
    product_fee     = Column(MmbBillCycleKeys.product_fee, Numeric(10, 2))
    product_currency= Column(MmbBillCycleKeys.product_currency, String(TableCharLimit._255))
    product_period  = Column(MmbBillCycleKeys.product_period, String(TableCharLimit._255))
    prod_start_at   = Column(MmbBillCycleKeys.prod_start_at, DateTime(True))
    
    next_cycle_at   = Column(MmbBillCycleKeys.next_cycle_at, DateTime(True))
    next_cycle_id   = Column(MmbBillCycleKeys.next_cycle_id, String(TableCharLimit._255))
    
    bill_cycle_id   = Column(MmbBillCycleKeys.bill_cycle_id, String(TableCharLimit._255))
    bill_cycle_start_at     = Column(MmbBillCycleKeys.bill_cycle_start_at, DateTime(True))
    bill_cycle_end_at       = Column(MmbBillCycleKeys.bill_cycle_end_at, DateTime(True))
    bill_cycle_charge_amount= Column(MmbBillCycleKeys.bill_cycle_charge_amount, Numeric(10, 2))
    bill_cycle_charge_currency= Column(MmbBillCycleKeys.bill_cycle_charge_currency, String(TableCharLimit._255))
    
    bill_cycle_blog_count   = Column(MmbBillCycleKeys.bill_cycle_blog_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_ques_count   = Column(MmbBillCycleKeys.bill_cycle_ques_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_ans_count    = Column(MmbBillCycleKeys.bill_cycle_ans_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_poll_count   = Column(MmbBillCycleKeys.bill_cycle_poll_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_poll_taken_count   = Column(MmbBillCycleKeys.bill_cycle_poll_taken_count, Integer, default= MmbBillCycleKeys.default_count)
    bill_cycle_actvy_count  = Column(MmbBillCycleKeys.bill_cycle_actvy_count, Integer, default= MmbBillCycleKeys.default_count)
    
    add_at                  = Column(MmbBillCycleKeys.add_at, DateTime(True),default= func.now(),  nullable= False)
    
Index('ix_member_id_add_at_desc', MmbBillCyclePrev.member_id, MmbBillCyclePrev.add_at.desc(), unique=True)
    



class MmbWaiver(Base):
    
    __tablename__   = MmbWaiverKeys.tablename
    __table_args__  = {'schema': MmbWaiverKeys.schema_mbr}
    
    id              = Column(MmbWaiverKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbWaiverKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    bill_cycle_id   = Column(MmbWaiverKeys.bill_cycle_id, String(TableCharLimit._255))
    calculated_at   = Column(MmbWaiverKeys.calculated_at, DateTime(True), default= func.now())
    
    blog_count      = Column(MmbWaiverKeys.blog_count, Integer)
    quest_count     = Column(MmbWaiverKeys.quest_count, Integer)
    ans_count       = Column(MmbWaiverKeys.ans_count, Integer)
    poll_count      = Column(MmbWaiverKeys.poll_count, Integer)
    poll_taken_count= Column(MmbWaiverKeys.poll_taken_count, Integer)
    activity_count  = Column(MmbWaiverKeys.activity_count, Integer)
    
    is_eligible     = Column(MmbWaiverKeys.is_eligible, Boolean)
    
Index('ix_member_id_waiver_calc_at', MmbWaiver.member_id, MmbWaiver.calculated_at.desc(), unique=True)








class MemberProfileHist(Base):
    
    __tablename__   = MemberProfileKeys.table_name_hist
    __table_args__  = {'schema': MemberProfileKeys.schema_mbr}
    
    id              = Column(MemberProfileKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MemberProfileKeys.id , UUID(as_uuid=True),nullable=False, index= True)
    apple_id        = Column(MemberProfileKeys.apple_id, String(TableCharLimit._255), nullable= True)
    apple_email     = Column(MemberProfileKeys.apple_email, String(TableCharLimit._255), nullable= True)
    google_id       = Column(MemberProfileKeys.google_id, String(TableCharLimit._255),  nullable= True)
    google_email    = Column(MemberProfileKeys.google_email, String(TableCharLimit._255), nullable= True)
    join_at         = Column(MemberProfileKeys.join_at, DateTime(True), nullable= False)
    
    alias           = Column(MemberProfileKeys.alias, String(TableCharLimit._255), nullable= True)
    alias_std       = Column(MemberProfileKeys.alias_std, String(TableCharLimit._255), nullable= True)

    bio             = Column(MemberProfileKeys.bio, String(TableCharLimit._255), nullable= True)
    image           = Column(MemberProfileKeys.image, String(TableCharLimit._255), nullable= True)
    gender          = Column(MemberProfileKeys.gender, String(TableCharLimit._255), nullable= True)
    is_dating       = Column(MemberProfileKeys.is_dating, Boolean, default=MemberProfileKeys.is_dating_default, nullable= True)
    
    add_at          = Column(MemberProfileKeys.add_at, DateTime(True), default= func.now())
    add_type        = Column(MemberProfileKeys.add_type, String(TableCharLimit._255), nullable= False)
    
Index('ix_prof_hist_member_id_add_at_desc', MemberProfileHist.member_id, MemberProfileHist.add_at.desc(), unique=True)


class MbrStatusCurr(Base):
    
    __tablename__ = MbrStatusKeys.table_name_curr
    __table_args__  = {'schema': MbrStatusKeys.schema_mbr}
    
    
    member_id       = Column(MbrStatusKeys.member_id, UUID(as_uuid=True), nullable= False, primary_key= True)

    member_status   = Column(MbrStatusKeys.member_status, Integer, index= True)
    
    product_id      = Column(MbrStatusKeys.product_id, String(TableCharLimit._255) , nullable= True)
    product_fee     = Column(MbrStatusKeys.product_fee, Numeric(10, 2), nullable= True)
    product_currency= Column(MbrStatusKeys.product_currency, String(TableCharLimit._255), nullable= True)
    product_period  = Column(MbrStatusKeys.product_period, String(TableCharLimit._255))
    
    is_banned       = Column(MbrStatusKeys.is_banned, Boolean, default= MbrStatusKeys.is_banned_default, index= True)
    update_at       = Column(MbrStatusKeys.update_at, DateTime(True), nullable= True)

class MbrStatusHist(Base):
    
    __tablename__ = MbrStatusKeys.table_name_hist
    __table_args__  = {'schema': MbrStatusKeys.schema_mbr}
    
    id              = Column(MbrStatusKeys.ID, BigInteger, primary_key= True)

    member_id       = Column(MbrStatusKeys.member_id, UUID(as_uuid=True), nullable= False)

    product_id      = Column(MbrStatusKeys.product_id, String(TableCharLimit._255) , nullable= True)
    product_fee     = Column(MbrStatusKeys.product_fee, Numeric(10, 2), nullable= True)
    product_currency= Column(MbrStatusKeys.product_currency, String(TableCharLimit._255), nullable= True)
    product_period  = Column(MbrStatusKeys.product_period, String(TableCharLimit._255))
    
    member_status   = Column(MbrStatusKeys.member_status, Integer)
    is_banned       = Column(MbrStatusKeys.is_banned, Boolean, default= MbrStatusKeys.is_banned_default)
    
    add_at          = Column(MbrStatusKeys.add_at, DateTime(True), default= func.now(), nullable= True)
    add_type        = Column(MbrStatusKeys.add_type, String(TableCharLimit._255))
    



class Languages(Base):
    
    __tablename__  = LanguageKeys.table_name
    __table_args__  = {'schema': MemberProfileKeys.schema_clb}

    id             = Column(LanguageKeys.id, SmallInteger,nullable=False, primary_key= True)
    name           = Column(LanguageKeys.name, String(TableCharLimit._255), nullable=False, unique=True)
    add_date       = Column(LanguageKeys.add_date, Date, default= current_time.date() , nullable= False)
    
class MemberLang(Base):
    
    __tablename__  = MmbLangKeys.table_name
    __table_args__  = {'schema': MemberProfileKeys.schema_mbr}
    
    id             = Column(MmbLangKeys.id, BigInteger, primary_key= True)
    member_id      = Column(MmbLangKeys.member_id, UUID(as_uuid=True), nullable= False, index = True)
    language_id    = Column(MmbLangKeys.language_id, SmallInteger, nullable= False, index= True)
    add_at         = Column(MmbLangKeys.add_at, DateTime(timezone= True), default= func.now(), nullable= False)
    
Index('ix_member_id_language_id', MemberLang.member_id, MemberLang.language_id)

class InterestAreas(Base):
    
    __tablename__ = InterestAreaKeys.table_name
    __table_args__  = {'schema': MemberProfileKeys.schema_clb}

    id            = Column(InterestAreaKeys.id, SmallInteger,nullable=False, primary_key= True)
    name          = Column(InterestAreaKeys.name, Text, nullable=False, unique=True)
    add_date      = Column(InterestAreaKeys.add_date, Date, default = current_time.date()  ,nullable= False)

class MemberIA(Base):
    
    __tablename__  = MmbIntAreaKeys.table_name
    __table_args__  = {'schema': MemberProfileKeys.schema_mbr}
    
    id             = Column(MmbIntAreaKeys.ID, BigInteger, primary_key= True)
    
    member_id      = Column(MmbIntAreaKeys.member_id, UUID(as_uuid=True), nullable= False, index= True)
    int_area_id    = Column(MmbIntAreaKeys.int_area_id, SmallInteger, nullable= False, index= True)
    add_at         = Column(MmbIntAreaKeys.add_at, DateTime(True), default= func.now(), nullable= False)
   
Index('ix_member_id_topic_id', MemberIA.member_id, MemberIA.int_area_id)

    
    
      
class SessionCurr(Base):
    
    __tablename__ = SignInKeys.table_name_curr
    __table_args__  = {'schema': SignInKeys.schema_mbr}
    
    id            = Column(SignInKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(SignInKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    signin_id     = Column(SignInKeys.signin_id, String(TableCharLimit._255), nullable= False)
    type          = Column(SignInKeys.type, String(TableCharLimit._255), nullable= False)
    ip            = Column(SignInKeys.ip, String(TableCharLimit._255), nullable= True)
    
    device_type   = Column(SignInKeys.device_type, String(TableCharLimit._255), nullable= True)
    device_model  = Column(SignInKeys.device_model, String(TableCharLimit._255), nullable= True)
    
    signin_at     = Column(SignInKeys.signin_at, DateTime(True), default= func.now(), nullable= False)
    
Index('ix_member_id_sign_in_at', SessionCurr.member_id, SessionCurr.signin_at.desc())
    
class SessionPrev(Base):
    
    __tablename__ = SignInKeys.table_name_prev
    __table_args__  = {'schema': SignInKeys.schema_mbr}
    
    id            = Column(SignInKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(SignInKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    signin_id     = Column(SignInKeys.signin_id, String(TableCharLimit._255), nullable= False)
    type          = Column(SignInKeys.type, String(TableCharLimit._255), nullable= False)
    ip            = Column(SignInKeys.ip, String(TableCharLimit._255), nullable= True)
    
    device_type   = Column(SignInKeys.device_type, String(TableCharLimit._255), nullable= True)
    device_model  = Column(SignInKeys.device_model, String(TableCharLimit._255), nullable= True)
    
    signin_at     = Column(SignInKeys.signin_at, DateTime(True), nullable= False)
    signout_at    = Column(SignInKeys.signout_at, DateTime(True), default= func.now() , nullable= False)
    
Index('ix_member_id_sign_out_at', SessionPrev.member_id, SessionPrev.signout_at.desc())




class MmbFollowCurr(Base):
    
    __tablename__  = MmbFollowKeys.table_name_curr
    __table_args__  = {'schema': MmbFollowKeys.schema_mbr}
    
    id               = Column(MmbFollowKeys.ID, BigInteger, primary_key= True)
    
    following_id     = Column(MmbFollowKeys.following_id, UUID(as_uuid=True), nullable= False, index= True)
    followed_id      = Column(MmbFollowKeys.followed_id, UUID(as_uuid=True), nullable= False, index= True)
    follow_at        = Column(MmbFollowKeys.follow_at, DateTime(True), default = func.now(), nullable= False)

class MmbFollowHist(Base):
    
    __tablename__   = MmbFollowKeys.table_name_prev
    __table_args__  = {'schema': MmbFollowKeys.schema_mbr}
    
    id               = Column(MmbFollowKeys.ID, BigInteger, primary_key= True)
    
    following_id     = Column(MmbFollowKeys.following_id, UUID(as_uuid=True), nullable= False, index= True)
    followed_id      = Column(MmbFollowKeys.followed_id, UUID(as_uuid=True), nullable= False, index= True)
    
    add_at           = Column(MmbFollowKeys.add_at, DateTime(True), default= func.now(), nullable= True)
    add_type         = Column(MmbFollowKeys.add_type, String(TableCharLimit._255))


    
    


class AliasHist(Base):
    
    __tablename__ = AliasHistKeys.table_name
    __table_args__  = {'schema': AliasHistKeys.schema_mbr}

    alias         = Column(AliasHistKeys.alias, Text, nullable=False, primary_key= True)
    add_at        = Column(AliasHistKeys.add_at, DateTime(True), default = func.now(), nullable= False)
    
    
    
    
class MmbMuteCurr(Base):
    
    __tablename__ =   MmbMuteKeys.table_name_curr
    __table_args__  = {'schema': MmbMuteKeys.schema_mbr}
    
    id              = Column(MmbMuteKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbMuteKeys.member_id, UUID(as_uuid=True), nullable= False)
    muted_mem_id    = Column(MmbMuteKeys.muted_mem_id, UUID(as_uuid=True), nullable= False)
    
    add_at          = Column(MmbMuteKeys.add_at, DateTime(True), default= func.now(), nullable= False)

Index('ix_member_id_muted_mbr_id', MmbMuteCurr.member_id, MmbMuteCurr.muted_mem_id)
    
class MmbMuteHist(Base):
    
    __tablename__ =   MmbMuteKeys.table_name_hist
    __table_args__  = {'schema': MmbMuteKeys.schema_mbr}
    
    id              = Column(MmbMuteKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbMuteKeys.member_id, UUID(as_uuid=True), nullable= False)
    muted_mem_id    = Column(MmbMuteKeys.muted_mem_id, UUID(as_uuid=True), nullable= False)
    
    add_type        = Column(MmbMuteKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(MmbMuteKeys.add_at, DateTime(True), default= func.now(), nullable= False)

Index('ix_member_id_muted_mbr_id_add_at', MmbMuteHist.member_id, MmbMuteHist.muted_mem_id, MmbMuteHist.add_at.desc())
    
 
   

class MmbSpamCurr(Base):
    
    __tablename__   =   MmbSpamKeys.table_name_curr
    __table_args__  = {'schema': MmbSpamKeys.schema_mbr}
    
    id              = Column(MmbSpamKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbSpamKeys.member_id, UUID(as_uuid=True), nullable= False)
    spam_mem_id     = Column(MmbSpamKeys.spam_mem_id, UUID(as_uuid=True), nullable= False)
    
    spam_at         = Column(MmbSpamKeys.spam_at, DateTime(True), default= func.now(), nullable= False)

Index('ix_member_id_spam_mbr_id', MmbSpamCurr.member_id, MmbSpamCurr.spam_mem_id)

class MmbSpamHist(Base):
    
    __tablename__   =   MmbSpamKeys.table_name_hist
    __table_args__  = {'schema': MmbSpamKeys.schema_mbr}
    
    id              = Column(MmbSpamKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbSpamKeys.member_id, UUID(as_uuid=True), nullable= False)
    spam_mem_id     = Column(MmbSpamKeys.spam_mem_id, UUID(as_uuid=True), nullable= False)
    
    add_type        = Column(MmbSpamKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(MmbSpamKeys.add_at, DateTime(True), default= func.now(), nullable= False)

Index('ix_member_id_spam_mbr_id_add_at', MmbSpamHist.member_id, MmbSpamHist.spam_mem_id, MmbSpamHist.add_at.desc())




class MmbReportHist(Base):
    
    __tablename__ = MmbReportKeys.table_name
    __table_args__  = {'schema': MmbReportKeys.schema_mbr}
    
    id             = Column(MmbReportKeys.ID, BigInteger, primary_key= True)
    
    reporting_id   = Column(MmbReportKeys.reporting_id, UUID(as_uuid=True), nullable= False, index= True)
    reported_id    = Column(MmbReportKeys.reported_id, UUID(as_uuid=True), nullable= False, index= True)
    
    content_type   = Column(MmbReportKeys.content_type, String(TableCharLimit._255), nullable= False)
    content_id     = Column(MmbReportKeys.content_id, String(TableCharLimit._255), nullable= True)
    content        = Column(MmbReportKeys.content, Text, nullable= True)
    
    reason_code    = Column(MmbReportKeys.reason_code, Integer, index= True)
    reason_other_text = Column(MmbReportKeys.reason_other_text, Text, nullable= True)

    report_at      = Column(MmbReportKeys.report_at, DateTime(True), nullable= False, default= func.now())

Index('ix_reported_content', MmbReportHist.content_type, MmbReportHist.content_id)

class ReportReason(Base):
    
    __tablename__ = ReprResKeys.tablename
    __table_args__  = {'schema': ReprResKeys.schema_clb}
    
    type    = Column(ReprResKeys.type, SmallInteger, primary_key= True)
    desc    = Column(ReprResKeys.desc, Text, nullable= False)
    



class MmbBanCurr(Base):

    __tablename__ =   MmbBanKeys.table_name_curr
    __table_args__  = {'schema': MmbBanKeys.schema_mbr}
    
    member_id       = Column(MmbBanKeys.member_id, UUID(as_uuid=True), nullable= False, primary_key= True)
    ban_by          = Column(MmbBanKeys.ban_by, SmallInteger, nullable= False)
    
    note            = Column(MmbBanKeys.note, Text, nullable= True)
    ban_at          = Column(MmbBanKeys.ban_at, DateTime(True), default= func.now(), nullable= False)
     
class MmbBanHist(Base):

    __tablename__ =   MmbBanKeys.table_name_hist
    __table_args__  = {'schema': MmbBanKeys.schema_mbr}
    
    id              = Column(MmbBanKeys.ID, BigInteger, primary_key= True)
    
    member_id       = Column(MmbBanKeys.member_id, UUID(as_uuid=True), nullable= False)
    add_by          = Column(MmbBanKeys.add_by, SmallInteger, nullable= False)
    
    note            = Column(MmbBanKeys.note, Text, nullable = True)
    
    add_type        = Column(MmbBanKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(MmbBanKeys.add_at, DateTime(True), default= func.now(), nullable= False)
     



class DailyQues(Base):
    
    __tablename__ = DailyQuesKeys.tablename
    __table_args__  = {'schema': DailyQuesKeys.schema_pst}
    
    id            = Column(DailyQuesKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    
    title         = Column(DailyQuesKeys.title, String(TableCharLimit._255))
    is_live       = Column(DailyQuesKeys.is_live, Boolean)
    
    add_dt        = Column(DailyQuesKeys.add_dt, Date, default= current_time.date())
    update_dt     = Column(DailyQuesKeys.update_dt, Date, default= current_time.date() )
      
class DailyAns(Base):
    
    __tablename__ = DailyAnsKeys.tablename
    __table_args__  = {'schema': DailyAnsKeys.schema_pst}
    
    id            = Column(DailyAnsKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    
    ques_id       = Column(DailyAnsKeys.ques_id, UUID(as_uuid=True), nullable= False)
    member_id     = Column(DailyAnsKeys.member_id, UUID(as_uuid=True), nullable= False, index= True)
    
    is_anonymous  = Column(DailyAnsKeys.is_anonymous, Boolean, default= 0)
    is_deleted    = Column(DailyAnsKeys.is_deleted, Boolean, default= 0)
    is_blocked    = Column(DailyAnsKeys.is_blocked, Boolean, default= 0)
    
    answer        = Column(DailyAnsKeys.answer, Text)
    post_at       = Column(DailyAnsKeys.post_at, DateTime(True), default= func.now() , index= True)
    
    block_by      = Column(DailyAnsKeys.block_by, String(TableCharLimit._255))
    block_note    = Column(DailyAnsKeys.block_note, Text)
    
    update_at     = Column(DailyAnsKeys.update_at, DateTime(True), default= func.now() )




class Post(Base):
    
    __tablename__ = PostKeys.table_name
    __table_args__  = {'schema': PostKeys.schema_pst}
    
    id            = Column(PostKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(PostKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    type          = Column(PostKeys.type, String(TableCharLimit._255), nullable= False)
    assc_post_id  = Column(PostKeys.assc_post_id, UUID(as_uuid=True), nullable= True)

    interest_id   = Column(PostKeys.interest_id, SmallInteger, nullable= True)
    lang_id       = Column(PostKeys.lang_id, SmallInteger, nullable= True)
    
    title         = Column(PostKeys.title, String(TableCharLimit._255), nullable= False)
    body          = Column(PostKeys.body, Text, nullable= False)
    
    tag1          = Column(PostKeys.tag1, String(TableCharLimit._255), nullable= True)
    tag2          = Column(PostKeys.tag2, String(TableCharLimit._255), nullable= True)
    tag3          = Column(PostKeys.tag3, String(TableCharLimit._255), nullable= True)
    
    tag1_std      = Column(PostKeys.tag1_std, String(TableCharLimit._255), nullable= True)
    tag2_std      = Column(PostKeys.tag2_std, String(TableCharLimit._255), nullable= True)
    tag3_std      = Column(PostKeys.tag3_std, String(TableCharLimit._255), nullable= True)
    
    post_at       = Column(PostKeys.posted_at, DateTime(True), default= func.now())
    
class PostDraft(Base):
    
    __tablename__ = PostDraftKeys.table_name
    __table_args__  = {'schema': PostDraftKeys.schema_pst}
    
    id            = Column(PostDraftKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(PostDraftKeys.member_id, UUID(as_uuid=True), nullable= False, index= True)
    
    assc_post_id  = Column(PostDraftKeys.assc_post_id, UUID(as_uuid=True), nullable= True)

    interest_id   = Column(PostDraftKeys.interest_id, SmallInteger, nullable= True)
    lang_id       = Column(PostDraftKeys.lang_id, SmallInteger, nullable= True)
    
    is_for_daily  = Column(PostDraftKeys.is_for_daily, Boolean, default= 0)
    
    type          = Column(PostDraftKeys.type, String(TableCharLimit._255), nullable= False)
    title         = Column(PostDraftKeys.title, String(TableCharLimit._255), nullable= True)
    body          = Column(PostDraftKeys.body, Text, nullable= True)

    save_at       = Column(PostDraftKeys.save_at, DateTime(True), default= func.now() ,nullable= False)




class PollQues(Base):
    
    __tablename__   = PollQuesKeys.table_name
    __table_args__  = {'schema': PollQuesKeys.schema_pst}
    
    poll_item_id    = Column(PollQuesKeys.poll_item_id, UUID(as_uuid=True), nullable=False, primary_key= True, server_default = default_uuid7)
    
    post_id         = Column(PollQuesKeys.post_id, UUID(as_uuid=True), nullable= False)
    
    ques_seq_id     = Column(PollQuesKeys.ques_seq_id, SmallInteger)
    ques_text       = Column(PollQuesKeys.ques_text, String(TableCharLimit._255))
    
    ans_seq_id      = Column(PollQuesKeys.ans_seq_id, SmallInteger)
    ans_text        = Column(PollQuesKeys.ans_text, String(TableCharLimit._255))
    
    create_at       = Column(PollQuesKeys.create_at, DateTime(True), default= func.now() )
    update_at       = Column(PollQuesKeys.update_at, DateTime(True), default= func.now() )

Index('ix_post_id_qstn_id_ans_id', PollQues.post_id, PollQues.ques_seq_id, PollQues.ans_seq_id)

class PollMemResult(Base):
    
    __tablename__   = PollMemResultKeys.tablename
    __table_args__  =     (
        # PrimaryKeyConstraint(PollMemResultKeys.poll_item_id, PollMemResultKeys.post_id, PollMemResultKeys.member_id),
        {'schema': PollMemResultKeys.schema_pst}
    )
    
    id              = Column(PollMemResultKeys.ID, BigInteger, primary_key= True)
    
    poll_item_id    = Column(PollMemResultKeys.poll_item_id, UUID(as_uuid=True), nullable=False)
    
    post_id         = Column(PollMemResultKeys.post_id, UUID(as_uuid=True), nullable= False, index= True)
    member_id       = Column(PollMemResultKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    taken_at        = Column(PollMemResultKeys.taken_at, DateTime(True), default= func.now() )


    
class PollInvite(Base):
    
    __tablename__   = PollInvKeys.tablename
    __table_args__  = {'schema': PollInvKeys.schema_pst}
    
    id              = Column(PollInvKeys.ID, BigInteger, primary_key= True)
    
    poll_post_id    = Column(PollInvKeys.poll_post_id, UUID(as_uuid=True), nullable=False, index= True)
    
    invite_at       = Column(PollInvKeys.invite_at, DateTime(True), default= func.now())
    
    inviting_mbr_id = Column(PollInvKeys.inviting_mbr_id, UUID(as_uuid=True), nullable=False, index= True)
    invited_mbr_id  = Column(PollInvKeys.invited_mbr_id, UUID(as_uuid=True), nullable=False, index= True)

class QuesInvite(Base):
    
    __tablename__   = QuesInvKeys.tablename
    __table_args__  = {'schema': QuesInvKeys.schema_pst}
    
    id              = Column(QuesInvKeys.ID, BigInteger, primary_key= True)
    
    ques_post_id    = Column(QuesInvKeys.ques_post_id, UUID(as_uuid=True), index= True)
    ans_post_id     = Column(QuesInvKeys.ans_post_id, UUID(as_uuid=True), nullable= True)
    
    invite_at       = Column(QuesInvKeys.invite_at, DateTime(True), default= func.now())
    
    inviting_mbr_id = Column(QuesInvKeys.inviting_mbr_id, UUID(as_uuid=True), nullable=False, index= True)
    invited_mbr_id  = Column(QuesInvKeys.invited_mbr_id, UUID(as_uuid=True), nullable=False, index= True)

class PostStatusCurr(Base):

    __tablename__ = PostStatusKeys.table_name_curr
    __table_args__  = {'schema': PostStatusKeys.schema_pst}
    
    post_id         = Column(PostStatusKeys.post_id, UUID(as_uuid=True), primary_key= True)

    is_anonymous    = Column(PostStatusKeys.is_anonymous, Boolean, default= PostStatusKeys.default_key)
    is_deleted      = Column(PostStatusKeys.is_deleted, Boolean, default= PostStatusKeys.default_key)
    
    is_blocked      = Column(PostStatusKeys.is_blocked, Boolean, default= PostStatusKeys.default_key)
    
    update_at       = Column(PostStatusKeys.update_at, DateTime(True) ,default= func.now())

class PostStatusHist(Base):
    
    __tablename__ = PostStatusKeys.table_name_hist
    __table_args__  = {'schema': PostStatusKeys.schema_pst}
    
    id              = Column(PostStatusKeys.ID, BigInteger, primary_key= True)
    
    post_id         = Column(PostStatusKeys.post_id, UUID(as_uuid=True), nullable= False)

    is_anonymous    = Column(PostStatusKeys.is_anonymous, Boolean, default= PostStatusKeys.default_key)
    is_deleted      = Column(PostStatusKeys.is_deleted, Boolean, default= PostStatusKeys.default_key)
    
    is_blocked      = Column(PostStatusKeys.is_blocked, Boolean, default= PostStatusKeys.default_key)
    
    add_at          = Column(PostStatusKeys.add_at, DateTime(True), default= func.now() )
    add_type        = Column(PostStatusKeys.add_type, String(TableCharLimit._255) ,nullable= False)




class PostBlockCurr(Base):

    __tablename__ =   PostBlockKeys.table_name_curr
    __table_args__  = {'schema': PostBlockKeys.schema_pst}
    
    post_id         = Column(PostBlockKeys.post_id, UUID(as_uuid=True), nullable= False, primary_key= True)
    note            = Column(PostBlockKeys.note, Text, nullable= True)
    
    block_by        = Column(PostBlockKeys.block_by, UUID(as_uuid=True), nullable= False)
    block_at        = Column(PostBlockKeys.block_at, DateTime(True), default= func.now()  ,nullable= False)

class PostBlockHist(Base):

    __tablename__ =   PostBlockKeys.table_name_hist
    __table_args__  = {'schema': PostBlockKeys.schema_pst}
    
    id              = Column(PostBlockKeys.ID, BigInteger, primary_key= True)
    
    post_id         = Column(PostBlockKeys.post_id, UUID(as_uuid=True), nullable= False)
    note            = Column(PostBlockKeys.note, Text, nullable= True)
    
    add_by          = Column(PostBlockKeys.add_by, UUID(as_uuid=True), nullable= False)
    
    add_at          = Column(PostBlockKeys.add_at, DateTime(True), default= func.now()  ,nullable= False)
    add_type        = Column(PostBlockKeys.add_type, String(TableCharLimit._255) ,nullable= False) 

Index('ix_post_id_add_at', PostBlockHist.post_id, PostBlockHist.add_at.desc())




class PostViews(Base):

    __tablename__   = PostViewKeys.tablename
    __table_args__  = (
        PrimaryKeyConstraint(PostViewKeys.post_id, PostViewKeys.view_at),
        {'schema': PostViewKeys.schema_pst}
    )
   
    post_id         = Column(PostViewKeys.post_id, UUID(as_uuid=True), nullable= False)
    view_at         = Column(PostViewKeys.view_at, DateTime(True),default= func.now()  ,nullable= False)
   
class PostViewCount(Base):

    __tablename__   = PostViewCntKeys.tablename
    __table_args__  = {'schema': PostViewCntKeys.schema_pst}
   
    post_id         = Column(PostViewCntKeys.post_id, UUID(as_uuid=True), primary_key= True) #one to one relation with a post, total view count is stored here, 
    count           = Column(PostViewCntKeys.count, Integer, nullable= False)
    
class PostLikeCurr(Base):
    
    __tablename__   = PostLikeKeys.table_name_curr
    __table_args__  = {'schema': PostLikeKeys.schema_pst}
    
    
    post_id         = Column(PostLikeKeys.post_id, UUID(as_uuid=True), primary_key= True)
    member_id       = Column(PostLikeKeys.member_id, UUID(as_uuid=True), nullable= False)

    like_at         = Column(PostLikeKeys.like_at, DateTime(True), default=func.now())

class PostLikeHist(Base):
    
    __tablename__   = PostLikeKeys.table_name_hist
    __table_args__  = {'schema': PostLikeKeys.schema_pst}
    
    id              = Column(PostLikeKeys.ID, BigInteger, primary_key= True)
    
    post_id         = Column(PostLikeKeys.post_id, UUID(as_uuid=True))
    member_id       = Column(PostLikeKeys.member_id, UUID(as_uuid=True), nullable= False)

    like_at         = Column(PostLikeKeys.like_at, DateTime(True))
    
    add_type        = Column(PostLikeKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(PostLikeKeys.add_at, DateTime(True), default=func.now())

class PostFavCurr(Base):
    
    __tablename__   = PostFavKeys.table_name_curr
    __table_args__  = {'schema': PostFavKeys.schema_pst}
    
    
    post_id         = Column(PostFavKeys.post_id, UUID(as_uuid=True), primary_key= True)
    member_id       = Column(PostFavKeys.member_id, UUID(as_uuid=True), nullable= False)

    fav_at          = Column(PostFavKeys.fav_at, DateTime(True), default=func.now())

class PostFavHist(Base):
    
    __tablename__   = PostFavKeys.table_name_hist
    __table_args__  = {'schema': PostFavKeys.schema_pst}
    
    id              = Column(PostFavKeys.ID, BigInteger, primary_key= True)
    
    post_id         = Column(PostFavKeys.post_id, UUID(as_uuid=True), primary_key= True)
    member_id       = Column(PostFavKeys.member_id, UUID(as_uuid=True), nullable= False)

    fav_at          = Column(PostFavKeys.fav_at, DateTime(True))
    
    add_type        = Column(PostFavKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(PostFavKeys.add_at, DateTime(True), default=func.now())

class PostFolCurr(Base):
    
    __tablename__   = PostFolKeys.table_name_curr
    __table_args__  = {'schema': PostFolKeys.schema_pst}
    
    
    post_id         = Column(PostFolKeys.post_id, UUID(as_uuid=True), primary_key= True)
    member_id       = Column(PostFolKeys.member_id, UUID(as_uuid=True), nullable= False)

    follow_at          = Column(PostFolKeys.follow_at, DateTime(True), default=func.now())

class PostFolHist(Base):
    
    __tablename__   = PostFolKeys.table_name_hist
    __table_args__  = {'schema': PostFolKeys.schema_pst}
    
    id              = Column(PostFolKeys.ID, BigInteger, primary_key= True)
    
    post_id         = Column(PostFolKeys.post_id, UUID(as_uuid=True), primary_key= True)
    member_id       = Column(PostFolKeys.member_id, UUID(as_uuid=True), nullable= False)

    follow_at       = Column(PostFolKeys.follow_at, DateTime)
    
    add_type        = Column(PostFolKeys.add_type, String(TableCharLimit._255), nullable= False)
    add_at          = Column(PostFolKeys.add_at, DateTime(True), default=func.now())





class TagList(Base):

    __tablename__   = TagListKeys.tablename
    __table_args__  = {'schema': TagListKeys.schema_pst}
        
    name            = Column(TagListKeys.name, String(TableCharLimit._255), nullable= False, primary_key= True)
    add_date        = Column(TagListKeys.add_date, Date, default= current_time.date())


   



class CommentNode(Base):
    
    __tablename__ = CommentNodeKeys.tablename
    __table_args__  = {'schema': CommentNodeKeys.schema_pst}
    
    comment_id      = Column(CommentNodeKeys.comment_id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    
    member_id       = Column(CommentNodeKeys.member_id, UUID(as_uuid=True), nullable= False)
    post_id         = Column(CommentNodeKeys.post_id, UUID(as_uuid=True), nullable= False, index= True)
    
    root_id         = Column(CommentNodeKeys.root_id, UUID(as_uuid=True), nullable=False, index= True)
    
    text            = Column(CommentNodeKeys.text, Text, nullable=False)
    is_deleted      = Column(CommentNodeKeys.is_deleted, Boolean, nullable=False, default= 0)
    
    create_at       = Column(CommentNodeKeys.create_at, DateTime(True), default=func.now())
    update_at       = Column(CommentNodeKeys.update_at, DateTime(True), default=func.now())
          
class CommentTree(Base):
    
    __tablename__ = CommentTreeKeys.tablename
    __table_args__  = (
        PrimaryKeyConstraint(CommentTreeKeys.parent_id, CommentTreeKeys.child_id),
        {'schema': CommentTreeKeys.schema_pst},
    )
    
    parent_id     = Column(CommentTreeKeys.parent_id, UUID(as_uuid=True), nullable= False)
    child_id      = Column(CommentTreeKeys.child_id, UUID(as_uuid=True), nullable= False)
    
    root_id       = Column(CommentTreeKeys.root_id, UUID(as_uuid=True), nullable=False, index= True)
    Depth         = Column(SmallInteger, nullable=False)

class DailyCommentNode(Base):
    
    __tablename__ = DailyCommentNodeKeys.tablename
    __table_args__  = {'schema': DailyCommentNodeKeys.schema_pst}
    
    comment_id      = Column(DailyCommentNodeKeys.comment_id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    
    member_id       = Column(DailyCommentNodeKeys.member_id, UUID(as_uuid=True), nullable= False)
    daily_answer_id = Column(DailyCommentNodeKeys.daily_answer_id, UUID(as_uuid=True), nullable= False, index= True)
    
    root_id         = Column(DailyCommentNodeKeys.root_id, UUID(as_uuid=True), nullable=False, index= True)
    
    text            = Column(DailyCommentNodeKeys.text, Text, nullable=False)
    is_deleted      = Column(DailyCommentNodeKeys.is_deleted, Boolean, nullable=False, default= 0)
    
    create_at       = Column(DailyCommentNodeKeys.create_at, DateTime(True), default=func.now())
    update_at       = Column(DailyCommentNodeKeys.update_at, DateTime(True), default=func.now())
          
class DailyCommentTree(Base):
    
    __tablename__ = DailyCommentTreeKeys.tablename
    __table_args__  = (
        PrimaryKeyConstraint(DailyCommentTreeKeys.parent_id, DailyCommentTreeKeys.child_id),
        {'schema': DailyCommentTreeKeys.schema_pst},
    )
    
    parent_id     = Column(DailyCommentTreeKeys.parent_id, UUID(as_uuid=True), nullable= False)
    child_id      = Column(DailyCommentTreeKeys.child_id, UUID(as_uuid=True), nullable= False)
    
    root_id       = Column(DailyCommentTreeKeys.root_id, UUID(as_uuid=True), nullable=False, index= True)
    Depth         = Column(SmallInteger, nullable=False)

class DailyAnsLike(Base):
    
    __tablename__ = DailyAnsLikeKeys.table_name
    __table_args__= {'schema': DailyAnsLikeKeys.schema_pst}
    
    id            = Column(DailyAnsLikeKeys.ID, BigInteger, primary_key= True)
    
    daily_answer_id    = Column(DailyAnsLikeKeys.daily_answer_id, UUID(as_uuid=True), nullable= False)
    member_id     = Column(DailyAnsLikeKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    like_at       = Column(DailyAnsLikeKeys.like_at, DateTime(True), default=func.now())


class DailyCmntLike(Base):
    
    __tablename__ = DailyCmntLikeKeys.table_name
    __table_args__= {'schema': DailyCmntLikeKeys.schema_pst}
    
    id            = Column(DailyCmntLikeKeys.ID, BigInteger, primary_key= True)
    
    comment_id    = Column(DailyCmntLikeKeys.comment_id, UUID(as_uuid=True), nullable= False)
    member_id     = Column(DailyCmntLikeKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    like_at       = Column(DailyCmntLikeKeys.like_at, DateTime(True), default=func.now())

class DailyPostShare(Base):
    
    __tablename__ = DailyAnsShareKeys.tablename
    __table_args__= {'schema': DailyAnsShareKeys.schema_pst}

    id          = Column(DailyAnsShareKeys.ID, BigInteger, primary_key= True)
    
    daily_answer_id     = Column(DailyAnsShareKeys.daily_answer_id, UUID(as_uuid=True), primary_key= True)
    share_mbr_id= Column(DailyAnsShareKeys.share_mbr_id, UUID(as_uuid=True), nullable= False)
    shared_to_id= Column(DailyAnsShareKeys.shared_to_id, UUID(as_uuid=True), nullable= True)
    
    share_at        = Column(DailyAnsShareKeys.share_at, DateTime(True), default=func.now())
    shared_to_type  = Column(DailyAnsShareKeys.shared_to_type, String(TableCharLimit._255))


class CommentLike(Base):
    
    __tablename__ = CommentLikeKeys.tablename
    __table_args__= {'schema': CommentLikeKeys.schema_pst}
    
    id            = Column(CommentLikeKeys.ID, BigInteger, primary_key= True)
    
    comment_id    = Column(CommentLikeKeys.comment_id, UUID(as_uuid=True), nullable= False)
    member_id     = Column(CommentLikeKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    like_at       = Column(CommentLikeKeys.like_at, DateTime(True), default=func.now())
    

class MmbMsgReport(Base):
    
    __tablename__ = MmbMsgReportKeys.tablename
    __table_args__= {'schema': MmbMsgReportKeys.schema_mbr}
    
    id          = Column(MmbMsgReportKeys.ID, BigInteger, primary_key= True)
    
    reported_member = Column(MmbMsgReportKeys.reported_member, UUID(as_uuid=True), nullable= False)
    reporting_member= Column(MmbMsgReportKeys.reporting_member, UUID(as_uuid=True), nullable= False)
    conversation_id = Column(MmbMsgReportKeys.conversation_id, String(TableCharLimit._255), nullable= False)
    reason_code     = Column(MmbMsgReportKeys.reason_code, SmallInteger, nullable= False, index= True)
    other_reason_text     = Column(MmbMsgReportKeys.other_reason_text, Text, nullable= True)
    report_at       = Column(MmbMsgReportKeys.report_at, DateTime(True), default=func.now())
    


class PostShare(Base):
    
    __tablename__ = PostShareKeys.tablename
    __table_args__= {'schema': PostShareKeys.schema_pst}

    id          = Column(PostShareKeys.ID, BigInteger, primary_key= True)
    
    post_id     = Column(PostShareKeys.post_id, UUID(as_uuid=True), primary_key= True)
    share_mbr_id= Column(PostShareKeys.share_mbr_id, UUID(as_uuid=True), nullable= False)
    shared_to_id= Column(PostShareKeys.shared_to_id, UUID(as_uuid=True), nullable= True)
    
    share_at        = Column(PostShareKeys.share_at, DateTime(True), default=func.now())
    shared_to_type  = Column(PostShareKeys.shared_to_type, String(TableCharLimit._255))
    



class ClubAdmin(Base):
    
    __tablename__ = ClubAdminKeys.tablename
    __table_args__= {'schema': ClubAdminKeys.schema_clb}
    
    admin_id      = Column(ClubAdminKeys.admin_id, SmallInteger, primary_key= True)

    first_name    = Column(ClubAdminKeys.first_name, Text)
    last_name     = Column(ClubAdminKeys.last_name, Text)
    
    start_dt      = Column(ClubAdminKeys.start_dt, Date)

class FeedbackLog(Base):
    
    __tablename__ = FeedbackKeys.tablename
    __table_args__= {'schema': FeedbackKeys.schema_clb}
    
    feedback_id   = Column(FeedbackKeys.feedback_id, BigInteger, primary_key= True)
    member_id     = Column(FeedbackKeys.member_id, SmallInteger, nullable= False)
    note_by       = Column(FeedbackKeys.note_by, UUID(as_uuid=True), nullable= True)
    
    detail        = Column(FeedbackKeys.detail, Text)
    
    email         = Column(FeedbackKeys.email, String(TableCharLimit._330))
    note          = Column(FeedbackKeys.note, Text, nullable= True)
    
    feedback_at   = Column(FeedbackKeys.feedback_at, DateTime(True), default=func.now())
    note_at       = Column(FeedbackKeys.note_at, DateTime(True))
    
    is_resolved   = Column(FeedbackKeys.is_resolved, Boolean, default= 0)
    


"""
class ViewDailyCmntLikeCnt(Base):
    
    __tablename__ = ViewDailyCmntLikeCntKeys.table_name
    __table_args__= {'schema': ViewDailyCmntLikeCntKeys.schema_pst}
    
    comment_id    = Column(ViewDailyCmntLikeCntKeys.comment_id, UUID(as_uuid=True),primary_key= True)
    like_cnt      = Column(ViewDailyCmntLikeCntKeys.like_cnt, default= 0)
    
    create_at     = Column(ViewDailyCmntLikeCntKeys.create_at, DateTime(True),default= func.now() )

class PromoOffer(Base):
    
    __tablename__   = PromoOfferKeys.tablename
    __table_args__  = (
        PrimaryKeyConstraint(PromoOfferKeys.ID, PromoOfferKeys.status),
        {'schema': PromoOfferKeys.schema_mbr}
    )
    
    
    id              = Column(PromoOfferKeys.ID, BigInteger, primary_key= True)
    member_id       = Column(PromoOfferKeys.member_id, UUID(as_uuid=True), nullable= False)

    offer_id        = Column(PromoOfferKeys.offer_id, String(TableCharLimit._255))
    bill_cycle_id   = Column(PromoOfferKeys.bill_cycle_id, String(TableCharLimit._255))
    
    type            = Column(PromoOfferKeys.type, String(TableCharLimit._255))
    disc_applied    = Column(PromoOfferKeys.disc_applied, Numeric(10, 2))
    disc_currency   = Column(PromoOfferKeys.disc_currency, String(TableCharLimit._255))
    
    assc_product    = Column(PromoOfferKeys.assc_product, String(TableCharLimit._255))
    
    offer_start_at  = Column(PromoOfferKeys.offer_start_at, DateTime)
    offer_end_at    = Column(PromoOfferKeys.offer_end_at, DateTime)
    
    status          = Column(PromoOfferKeys.status, String(TableCharLimit._255), default= 'A')
    redeemed_at     = Column(PromoOfferKeys.redeemed_at, DateTime, default = None ,nullable= True)
    
    create_by       = Column(PromoOfferKeys.create_by, String(TableCharLimit._255), default= PromoOfferKeys.default_create_by)
    update_at       = Column(PromoOfferKeys.update_at, DateTime(True), default = None)

class ViewMemFollowers(Base):

    __tablename__   = ViewMemFollKeys.table_name
    __table_args__  = {'schema': ViewMemFollKeys.schema_mbr}
        
    member_id       = Column(ViewMemFollKeys.member_id, UUID(as_uuid=True), nullable= False, primary_key= True)
    
    following       = Column(ViewMemFollKeys.following, Integer, nullable= False)
    follower        = Column(ViewMemFollKeys.follower, Integer, nullable= False)
    
    add_at           = Column(ViewMemFollKeys.create_at, DateTime(True), default= func.now(), nullable= True)


class ViewCommentLikeCount(Base):
    
    __tablename__ = ViewCmntLikeCntKeys.tablename
    __table_args__= {'schema': ViewCmntLikeCntKeys.schema_pst}
    
    comment_id    = Column(ViewCmntLikeCntKeys.comment_id, UUID(as_uuid=True), primary_key= True)
    count         = Column(ViewCmntLikeCntKeys.count, SmallInteger)
    
    create_at     = Column(ViewCmntLikeCntKeys.create_at, DateTime(True), default=func.now())


class ViewPostScore(Base):
    
    __tablename__   = ViewPostScoreKeys.tablename
    __table_args__  = {'schema': ViewPostScoreKeys.schema_pst}

    post_id         = Column(ViewPostScoreKeys.post_id, UUID(as_uuid=True), primary_key= True)

    view_count      = Column(ViewPostScoreKeys.view_count, Integer, default= 0)
    comment_cnt     = Column(ViewPostScoreKeys.comment_cnt, Integer, default= 0)
    like_cnt        = Column(ViewPostScoreKeys.like_cnt, Integer, default= 0)
    favorite_cnt    = Column(ViewPostScoreKeys.favorite_cnt, Integer, default= 0)
    follow_cnt      = Column(ViewPostScoreKeys.follow_cnt, Integer, default= 0)
    answer_cnt      = Column(ViewPostScoreKeys.answer_cnt, Integer, default= 0)
    poll_entry_cnt  = Column(ViewPostScoreKeys.poll_entry_cnt, Integer, default= 0)
    share_cnt       = Column(ViewPostScoreKeys.share_cnt, Integer, default= 0)
    report_cnt      = Column(ViewPostScoreKeys.report_cnt, Integer, default= 0)
    
    post_score      = Column(ViewPostScoreKeys.post_score, Integer, default= 0)
    
    create_at       = Column(ViewPostScoreKeys.create_at, DateTime(True), default=func.now())


class ViewMmbTag(Base):
    
    __tablename__   = ViewMmbTagKeys.tablename
    __table_args__  = {'schema': ViewMmbTagKeys.schema_pst}
    
    id              = Column(ViewMmbTagKeys.ID, BigInteger, primary_key= True)
    member_id       = Column(ViewMmbTagKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    tag_std         = Column(ViewMmbTagKeys.tag_std, String(TableCharLimit._255), nullable=False)
    count           = Column(ViewMmbTagKeys.count, Integer, nullable=False)


class ViewDailyPostScore(Base):
    
    __tablename__   = ViewDailyPostScoreKeys.tablename
    __table_args__  = {'schema': ViewDailyPostScoreKeys.schema_pst}

    answer_id       = Column(ViewDailyPostScoreKeys.answer_id, UUID(as_uuid=True), primary_key= True)

    view_count      = Column(ViewDailyPostScoreKeys.view_count, Integer, default= 0)
    comment_cnt     = Column(ViewDailyPostScoreKeys.comment_cnt, Integer, default= 0)
    like_cnt        = Column(ViewDailyPostScoreKeys.like_cnt, Integer, default= 0)
    favorite_cnt    = Column(ViewDailyPostScoreKeys.favorite_cnt, Integer, default= 0)

    share_cnt       = Column(ViewDailyPostScoreKeys.share_cnt, Integer, default= 0)
    report_cnt      = Column(ViewDailyPostScoreKeys.report_cnt, Integer, default= 0)
    
    post_score      = Column(ViewDailyPostScoreKeys.post_score, Integer, default= 0)
    
    create_at       = Column(ViewDailyPostScoreKeys.create_at, DateTime(True),default= func.now() )
    
    
class PollResult(Base):
    
    __tablename__   = PollResultKeys.tablename
    __table_args__  = {'schema': PollResultKeys.schema_pst}
    
    poll_item_id    = Column(PollResultKeys.poll_item_id, UUID(as_uuid=True), nullable=False, primary_key= True)

    count           = Column(PollResultKeys.count, Integer)
    total_qstn_entry_count  = Column(PollResultKeys.total_qstn_entry_count, Integer) #To help calculating answer choice %

"""


view_mem_fol_cnt_sql = """
CREATE MATERIALIZED VIEW mbr.v_mbr_follow_cnt 
WITH (FILLFACTOR = 70) AS
-- Main query to select member follow counts
SELECT 
    mbr.mbr_id AS mbr_id,
    COALESCE(flwing.following_cnt, 0) AS following_cnt,
    COALESCE(flwer.follower_cnt, 0) AS follower_cnt,
    CURRENT_TIMESTAMP AS create_at
FROM 
    mbr.mbr_profile_curr mbr
LEFT JOIN 
    -- Subquery to count following members
    (
        SELECT 
            following_mbr_id AS member_id, 
            COUNT(*) AS following_cnt
        FROM 
            mbr.mbr_follow_curr
        GROUP BY 
            following_mbr_id
    ) flwing ON mbr.mbr_id = flwing.member_id
LEFT JOIN 
    -- Subquery to count followers
    (
        SELECT 
            followed_mbr_id AS member_id, 
            COUNT(*) AS follower_cnt
        FROM 
            mbr.mbr_follow_curr
        GROUP BY 
            followed_mbr_id
    ) flwer ON mbr.mbr_id = flwer.member_id;

-- Create a unique index on member ID to improve query performance
CREATE UNIQUE INDEX idx_v_mbr_follow_cnt_mbr_id ON mbr.v_mbr_follow_cnt (mbr_id);

"""
# REFRESH MATERIALIZED VIEW CONCURRENTLY mbr.v_mbr_follow_cnt;

view_cmnt_like_sql = """

CREATE MATERIALIZED VIEW pst.v_post_comment_like_cnt 
WITH (FILLFACTOR = 70) AS
-- Main query to select comment like counts
SELECT 
    comment_id, 
    COUNT(*) AS like_cnt,
    NOW() AS create_at
FROM 
    pst.mbr_comment_like
GROUP BY 
    comment_id;

-- Create a unique index on comment ID to improve query performance
CREATE UNIQUE INDEX idx_v_post_comment_like_cnt_comment_id ON pst.v_post_comment_like_cnt (comment_id);


"""
# REFRESH MATERIALIZED VIEW CONCURRENTLY pst.v_post_comment_like_cnt;
    
view_post_score_sql = """

CREATE MATERIALIZED VIEW pst.v_post_score 
WITH (FILLFACTOR = 70) AS
WITH 
-- Subquery to count comments for each post
comment_cnts AS (
    SELECT 
        post_id, 
        COUNT(*) AS comment_cnt
    FROM 
        pst.post_comment_node
    GROUP BY 
        post_id
),
-- Subquery to count comments on answers associated with questions
qstn_answ_comment_cnts AS (
    SELECT 
        q.assoc_qstn_post_id, 
        COUNT(*) AS answ_comment_cnt
    FROM 
        pst.post_posted q
    JOIN 
        pst.post_comment_node c ON q.post_id = c.post_id
    WHERE 
        q.post_type = 'A'
    GROUP BY 
        q.assoc_qstn_post_id
),
-- Subquery to count poll entries for each poll post
poll_entry_cnts AS (
    SELECT 
        pr.poll_post_id,
        COUNT(DISTINCT poll_post_id) AS poll_entry_cnt
    FROM 
        pst.mbr_poll_result pr 
    GROUP BY 
        pr.poll_post_id
),
-- Subquery to count likes for each post
like_cnts AS (
    SELECT 
        post_id, 
        COUNT(*) AS like_cnt
    FROM 
        pst.post_like_curr 
    GROUP BY 
        post_id
),
-- Subquery to count likes on answers associated with questions
qstn_answ_like_cnts AS (
    SELECT 
        q.assoc_qstn_post_id, 
        COUNT(*) AS answ_like_cnt
    FROM 
        pst.post_posted q
    JOIN 
        pst.post_like_curr l ON q.post_id = l.post_id
    WHERE 
        q.post_type = 'A'
    GROUP BY 
        q.assoc_qstn_post_id
),
-- Subquery to count favorites for each post
fav_cnts AS (
    SELECT 
        post_id, 
        COUNT(*) AS fav_cnt
    FROM 
        pst.post_fav_curr 
    GROUP BY 
        post_id
),
-- Subquery to count favorites on answers associated with questions
qstn_answ_fav_cnts AS (
    SELECT 
        q.assoc_qstn_post_id, 
        COUNT(*) AS answ_fav_cnt
    FROM 
        pst.post_posted q
    JOIN 
        pst.post_fav_curr f ON q.post_id = f.post_id
    WHERE 
        q.post_type = 'A'
    GROUP BY 
        q.assoc_qstn_post_id
),
-- Subquery to count answers for each question
answer_cnts AS (
    SELECT 
        assoc_qstn_post_id, 
        COUNT(*) AS answer_cnt
    FROM 
        pst.post_posted q
    GROUP BY 
        assoc_qstn_post_id
),
-- Subquery to count follows for each post
follow_cnts AS (
    SELECT 
        post_id, 
        COUNT(*) AS follow_cnt
    FROM 
        pst.post_follow_curr
    GROUP BY 
        post_id
),
-- Subquery to count shares for each post
share_cnts AS (
    SELECT 
        post_id, 
        COUNT(*) AS share_cnt
    FROM 
        pst.post_share 
    GROUP BY 
        post_id
),
-- Subquery to count reports for each post
report_cnts AS (
    SELECT 
        content_id, 
        COUNT(*) AS report_cnt
    FROM 
        mbr.mbr_report_hist
    WHERE 
        content_type = 'P'
    GROUP BY 
        content_id
),
-- Main CTE to calculate all necessary counts and the final post score
post_scores AS (
    SELECT 
        p.post_id, 
        p.post_type,
        COALESCE(pvc.view_cnt, 0) AS pst_view_cnt,
        CASE 
            WHEN p.post_type = 'Q' THEN COALESCE(cc.comment_cnt, 0) + COALESCE(qcc.answ_comment_cnt, 0)
            ELSE COALESCE(cc.comment_cnt, 0) 
        END AS pst_comment_cnt,
        CASE 
            WHEN p.post_type = 'Q' THEN COALESCE(lc.like_cnt, 0) + COALESCE(qlc.answ_like_cnt, 0)
            ELSE COALESCE(lc.like_cnt, 0) 
        END AS pst_like_cnt,
        CASE 
            WHEN p.post_type = 'Q' THEN COALESCE(fc.fav_cnt, 0) + COALESCE(qfc.answ_fav_cnt, 0)
            ELSE COALESCE(fc.fav_cnt, 0) 
        END AS pst_fav_cnt,
        COALESCE(fc2.follow_cnt, 0) AS pst_follow_cnt,
        COALESCE(ac.answer_cnt, 0) AS pst_answer_cnt,
        COALESCE(pec.poll_entry_cnt, 0) AS pst_poll_entry_cnt,
        COALESCE(sc.share_cnt, 0) AS pst_share_cnt,
        COALESCE(rc.report_cnt, 0) AS pst_report_cnt,
        NOW() AS create_at
    FROM 
        pst.post_posted p
    LEFT JOIN 
        pst.post_view_cnt pvc ON p.post_id = pvc.post_id
    LEFT JOIN 
        comment_cnts cc ON p.post_id = cc.post_id
    LEFT JOIN 
        qstn_answ_comment_cnts qcc ON p.post_id = qcc.assoc_qstn_post_id
    LEFT JOIN 
        like_cnts lc ON p.post_id = lc.post_id
    LEFT JOIN 
        qstn_answ_like_cnts qlc ON p.post_id = qlc.assoc_qstn_post_id
    LEFT JOIN 
        fav_cnts fc ON p.post_id = fc.post_id
    LEFT JOIN 
        qstn_answ_fav_cnts qfc ON p.post_id = qfc.assoc_qstn_post_id
    LEFT JOIN 
        follow_cnts fc2 ON p.post_id = fc2.post_id
    LEFT JOIN 
        share_cnts sc ON p.post_id = sc.post_id
    LEFT JOIN 
        report_cnts rc ON p.post_id::TEXT = rc.content_id
    LEFT JOIN 
        poll_entry_cnts pec ON p.post_id = pec.poll_post_id
    LEFT JOIN 
        answer_cnts ac ON p.post_id = ac.assoc_qstn_post_id
)
-- Final SELECT from post_scores CTE
SELECT 
    post_id, 
    post_type,
    pst_view_cnt,
    pst_comment_cnt,
    pst_like_cnt,
    pst_fav_cnt,
    pst_follow_cnt,
    pst_answer_cnt,
    pst_poll_entry_cnt,
    pst_share_cnt,
    pst_report_cnt,
    (
        (pst_view_cnt * 0.05)::bigint +
        pst_comment_cnt * 5 +
        pst_like_cnt +
        pst_fav_cnt * 5 +
        pst_follow_cnt * 5 +
        pst_answer_cnt * 10 +
        pst_poll_entry_cnt * 5 +
        pst_share_cnt * 2 -
        pst_report_cnt * 5
    ) AS post_score,
    create_at
FROM 
    post_scores;

-- Create indexes to improve query performance
CREATE UNIQUE INDEX idx_v_post_score_post_id ON pst.v_post_score (post_id);
CREATE UNIQUE INDEX idx_v_post_score_post_id_answ0 ON pst.v_post_score (post_id) WHERE post_type != 'A';


"""
# REFRESH MATERIALIZED VIEW CONCURRENTLY pst.v_post_score;

view_mmb_tags_sql = """

CREATE MATERIALIZED VIEW pst.v_mbr_tag_cnt 
WITH (FILLFACTOR = 70) AS
SELECT 
    row_number() OVER (ORDER BY tag_std, lst_at DESC, mbr_id) AS id,
    tag_std AS df_tag_std,
    mbr_id,
    tag_cnt,
    fst_at,
    lst_at,
    CURRENT_TIMESTAMP AS create_at
FROM (
    SELECT
        mbr_id,
        tag_std,
        COUNT(*) AS tag_cnt,
        MIN(post_at) AS fst_at,
        MAX(post_at) AS lst_at
    FROM (
        SELECT 
            mbr_id,
            tag1_std AS tag_std,
            post_at
        FROM pst.post_posted 
        WHERE tag1_std IS NOT NULL
        UNION ALL
        SELECT 
            mbr_id,
            tag2_std AS tag_std,
            post_at
        FROM pst.post_posted
        WHERE tag2_std IS NOT NULL
        UNION ALL
        SELECT 
            mbr_id,
            tag3_std AS tag_std,
            post_at
        FROM pst.post_posted
        WHERE tag3_std IS NOT NULL
    ) tags
    GROUP BY mbr_id, tag_std
) AS mbr_tag;

CREATE INDEX idx_v_mbr_tag_cnt_df_tag_std_lst_at_d ON pst.v_mbr_tag_cnt (df_tag_std, lst_at DESC);
CREATE INDEX idx_v_mbr_tag_cnt_mbr_id ON pst.v_mbr_tag_cnt (mbr_id);

"""

view_daily_ans_cmnt_like_sql = """

CREATE MATERIALIZED VIEW pst.v_daily_answer_comment_like_cnt
WITH (FILLFACTOR = 70) AS
SELECT comment_id, count(*) AS like_cnt,
   now() AS create_at
   FROM pst.mbr_daily_answer_comment_like
  GROUP BY comment_id;
  
CREATE UNIQUE INDEX idx_v_daily_answer_comment_like_cnt_comment_id on pst.v_daily_answer_comment_like_cnt (comment_id);

"""

# REFRESH MATERIALIZED VIEW CONCURRENTLY pst.v_daily_answer_comment_like_cnt;

view_daily_ans_score_sql = """
CREATE MATERIALIZED VIEW pst.v_daily_answer_score 
WITH (FILLFACTOR = 60) AS

-- Main query to calculate the daily answer score
SELECT 
    a.daily_answer_id,
    COALESCE(vc.view_cnt, 0) AS view_cnt,
    COALESCE(cc.cnt, 0) AS comment_cnt,
    COALESCE(lc.cnt, 0) AS like_cnt,
    COALESCE(sc.cnt, 0) AS share_cnt,
    COALESCE(rc.cnt, 0) AS report_cnt,
    (
        (COALESCE(vc.view_cnt, 0) * 0.05)::bigint +
        COALESCE(cc.cnt, 0) * 5 +
        COALESCE(lc.cnt, 0) +
        COALESCE(sc.cnt, 0) * 2 +
        (COALESCE(rc.cnt, 0) * -5)
    ) AS post_score,
    CURRENT_TIMESTAMP AS create_at
FROM 
    pst.daily_answer_posted a
LEFT JOIN 
    pst.post_view_cnt vc ON a.daily_answer_id = vc.post_id
LEFT JOIN 
    (
        SELECT daily_answer_id, COUNT(*) AS cnt
        FROM pst.daily_answer_comment_node 
        GROUP BY daily_answer_id
    ) cc ON a.daily_answer_id = cc.daily_answer_id
LEFT JOIN 
    (
        SELECT daily_answer_id, COUNT(*) AS cnt
        FROM pst.daily_answer_like_curr
        GROUP BY daily_answer_id
    ) lc ON a.daily_answer_id = lc.daily_answer_id
LEFT JOIN 
    (
        SELECT daily_answer_id, COUNT(*) AS cnt
        FROM pst.daily_answer_share 
        GROUP BY daily_answer_id
    ) sc ON a.daily_answer_id = sc.daily_answer_id
LEFT JOIN 
    (
        SELECT content_id, COUNT(*) AS cnt
        FROM mbr.mbr_report_hist  
        WHERE content_type = 'A'
        GROUP BY content_id
    ) rc ON a.daily_answer_id::TEXT = rc.content_id;

-- Create a unique index on daily_answer_id to improve query performance
CREATE UNIQUE INDEX idx_v_daily_answer_score_daily_answer_id ON pst.v_daily_answer_score (daily_answer_id);

"""


view_poll_result_sql = """

CREATE OR REPLACE VIEW pst.v_poll_result AS
WITH choice_counts AS (
    SELECT
        pmr.poll_item_id,
        COUNT(pmr.mbr_id) AS entry_cnt
    FROM
        pst.mbr_poll_result pmr
    GROUP BY
        pmr.poll_item_id
),
question_totals AS (
    SELECT
        pq.poll_item_id,
        pq.qstn_seq_id,
        COUNT(DISTINCT pmr.mbr_id) AS qstn_ttl_entry_cnt
    FROM
        pst.poll_detail pq
    LEFT JOIN
        pst.mbr_poll_result pmr ON pq.poll_item_id = pmr.poll_item_id
    GROUP BY
        pq.poll_item_id, pq.qstn_seq_id
)
SELECT
    pq.poll_item_id,
    COALESCE(cc.entry_cnt, 0) AS entry_cnt,
    COALESCE(qt.qstn_ttl_entry_cnt, 0) AS qstn_ttl_entry_cnt
FROM
    pst.poll_detail pq
LEFT JOIN
    choice_counts cc ON pq.poll_item_id = cc.poll_item_id
LEFT JOIN
    question_totals qt ON pq.poll_item_id = qt.poll_item_id AND pq.qstn_seq_id = qt.qstn_seq_id
GROUP BY
    pq.poll_item_id, cc.entry_cnt, qt.qstn_ttl_entry_cnt;

"""


promo_offer_sql = """
CREATE TABLE mbr.mbr_promo_offer_hist (
        id BIGSERIAL NOT NULL,
        mbr_id UUID NOT NULL,
        offer_id VARCHAR(255),
        bill_cycle_id VARCHAR(255),
        offer_type VARCHAR(255),
        discnt_amt_or_pct NUMERIC(10, 2),
        discnt_currency VARCHAR(255),
        assoc_prod VARCHAR(255),
        offer_start_at TIMESTAMP,
        offer_end_at TIMESTAMP,
        redeem_status VARCHAR(255) DEFAULT 'A',
        redeem_at TIMESTAMP DEFAULT NULL,
        create_by VARCHAR(255) DEFAULT 'system',
        update_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
        PRIMARY KEY (id, redeem_status)
    ) PARTITION BY LIST (redeem_status);
	
CREATE TABLE mbr.promo_offer_active PARTITION OF mbr.mbr_promo_offer_hist
    FOR VALUES IN ('A');
	
CREATE TABLE mbr.promo_offer_expired PARTITION OF mbr.mbr_promo_offer_hist
    FOR VALUES IN ('E');
	
CREATE TABLE mbr.promo_offer_redeemed PARTITION OF mbr.mbr_promo_offer_hist
    FOR VALUES IN ('R');
"""

"""
with engine.connect() as connection:
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS mbr"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS clb"))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS pst"))
    
    connection.commit()
    connection.close()

Base.metadata.create_all(bind=engine)

with engine.connect() as connection:
    
    
    connection.execute(text(promo_offer_sql))
    
    connection.execute(text(view_mem_fol_cnt_sql))
    connection.execute(text(view_cmnt_like_sql))
    connection.execute(text(view_post_score_sql))
    connection.execute(text(view_mmb_tags_sql))
    connection.execute(text(view_daily_ans_score_sql))
    connection.execute(text(view_poll_result_sql))
    connection.execute(text(view_daily_ans_cmnt_like_sql))

    connection.commit()
"""