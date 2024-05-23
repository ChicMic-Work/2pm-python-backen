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
from utilities.constants import current_time

from sqlalchemy import (
    Boolean, Column, Integer, String, SmallInteger, 
    DateTime, UUID, text, LargeBinary,
    ForeignKey, Table,
    CheckConstraint, Index,
    DDL, event, Date
    )

from database.table_keys import (
    MemberProfileKeys, MmbLangKeys,
    LanguageKeys, MmbIntAreaKeys,
    InterestAreaKeys, MemberStatusKeys,
    SignInKeys, PromoOfferKeys,
    MemFavRecKeys, MemTotalPostKeys,
    MemInvitesKeys, PostKeys,
    MemSubKeys, MemAliasHistKeys,
    AliasHistKeys, 
    
)

from sqlalchemy.orm import validates, relationship

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:1234@postgres:5432/2pm_ML1"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,)
SessionLocal = async_sessionmaker(bind= engine, autocommit=False, autoflush=False, class_= AsyncSession )

Base = declarative_base()

default_uuid7 = text("uuid_generate_v7()")

member_language_association = Table(
    MmbLangKeys.table_name,
    Base.metadata,
    Column(MmbLangKeys.id, Integer, primary_key= True),
    Column(MmbLangKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK)),
    Column(MmbLangKeys.language_id, SmallInteger, ForeignKey(LanguageKeys.lang_id_FK)),
    Column(MmbLangKeys.add_at, Date, default= current_time.date())
)

member_interest_area_association = Table(
    MmbIntAreaKeys.table_name,
    Base.metadata,
    Column(MmbIntAreaKeys.id, Integer, primary_key= True),
    Column(MmbIntAreaKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK)),
    Column(MmbIntAreaKeys.int_area_id, SmallInteger, ForeignKey(InterestAreaKeys.int_id_FK)),
    Column(MmbIntAreaKeys.add_at, Date, default= current_time.date())
)

class MemberProfile(Base):
    __tablename__   = MemberProfileKeys.table_name
    id              = Column(MemberProfileKeys.id , UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    apple_id        = Column(MemberProfileKeys.apple_id, String, unique=True, index=True)
    google_id       = Column(MemberProfileKeys.google_id, String, unique=True, index=True)
    join_at         = Column(MemberProfileKeys.join_at, DateTime, default= current_time, nullable= False)
    
    alias           = Column(MemberProfileKeys.alias, String, unique=True, index=True)
    bio             = Column(MemberProfileKeys.bio, String)
    image           = Column(MemberProfileKeys.image, String)
    gender          = Column(MemberProfileKeys.gender, String)
    is_dating       = Column(MemberProfileKeys.is_dating, Boolean, default=MemberProfileKeys.is_dating_default)
    
    add_at          = Column(MemberProfileKeys.add_at, Date, nullable= True)
    is_current      = Column(MemberProfileKeys.is_current, Boolean, nullable= False, default= 1)
    
    member_posts            = relationship(PostKeys.py_table_name, back_populates=PostKeys._memb)
    member_sub              = relationship(MemSubKeys.py_table_name, back_populates=MemSubKeys._memb)

    language_choices        = relationship(LanguageKeys.py_table_name, secondary = member_language_association, back_populates= MemberProfileKeys._lang)
    interest_area_choices   = relationship(InterestAreaKeys.py_table_name, secondary = member_interest_area_association, back_populates= MemberProfileKeys._int_area)
    
    status                  = relationship(MemberStatusKeys.py_table_name, uselist=False, back_populates=MemberStatusKeys._memb)
    session                 = relationship(SignInKeys.py_table_name, back_populates=SignInKeys._memb)
    
    favorite_like_received  = relationship(MemFavRecKeys.py_table_name, uselist=False, back_populates=MemFavRecKeys._memb)
    post_invites            = relationship(MemInvitesKeys.py_table_name, uselist=False, back_populates=MemInvitesKeys._memb)
    total_post_count        = relationship(MemTotalPostKeys.py_table_name, uselist=False, back_populates=MemTotalPostKeys._memb)
    
    member_alias_hist       = relationship(MemAliasHistKeys.py_table_name, back_populates=MemAliasHistKeys._memb)
    
    # @validates("gender")
    # def validate_gender(self, key, value):
    #     assert value in MemberProfileKeys.gender_validation, f"Invalid gender: {value}"
    #     return value
    
Index('ix_apple_id_unique', MemberProfile.apple_id, unique=True, postgresql_where=MemberProfile.apple_id.isnot(None))
Index('ix_alias_unique', MemberProfile.alias, unique=True, postgresql_where=MemberProfile.alias.isnot(None))
Index('ix_google_id_unique', MemberProfile.google_id, unique=True, postgresql_where=MemberProfile.google_id.isnot(None))

partition_by_is_current = DDL(f"""
    ALTER TABLE {MemberProfileKeys.table_name}
    PARTITION BY LIST ({MemberProfileKeys.is_current})
""")

create_partition_is_current_true = DDL(f"""
    CREATE TABLE {MemberProfileKeys._table_name_curr} PARTITION OF {MemberProfileKeys.table_name}
    FOR VALUES IN (true)
""")

create_partition_is_current_false = DDL(f"""
    CREATE TABLE {MemberProfileKeys._table_name_prev} PARTITION OF {MemberProfileKeys.table_name}
    FOR VALUES IN (false)
""")

# event.listen(MemberProfile, 'after_create', partition_by_is_current)
# event.listen(MemberProfile, 'after_create', create_partition_is_current_true)
# event.listen(MemberProfile, 'after_create', create_partition_is_current_false)

""" 
    __table_args__ = (
        CheckConstraint(
            f"({MemberProfileKeys.apple_id.lower()} IS NULL AND {MemberProfileKeys.google_id.lower()} IS NOT NULL) OR ({MemberProfileKeys.apple_id.lower()} IS NOT NULL AND {MemberProfileKeys.google_id.lower()} IS NULL)",
            name="chk_either_apple_or_google_id_null"
        ),
    )
    
    __table_args__ = (
        CheckConstraint(
            f"(({MemberProfileKeys.column_with_tn(MemberProfileKeys.apple_id)}) IS NULL AND ({MemberProfileKeys.column_with_tn(MemberProfileKeys.google_id)}) IS NOT NULL) OR (({MemberProfileKeys.column_with_tn(MemberProfileKeys.apple_id)}) IS NOT NULL AND ({MemberProfileKeys.column_with_tn(MemberProfileKeys.google_id)}) IS NULL)",
            name="chk_either_apple_or_google_id_null"
        ),
    )
""" 
    

class MemSub(Base):
    __tablename__ = MemSubKeys.table_name

    id            = Column(MemSubKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemSubKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    
    memb_sub_level  = Column(MemSubKeys.memb_sub_level, SmallInteger, nullable= False)
    memb_sub_status = Column(MemSubKeys.memb_sub_status, SmallInteger, nullable= False)
    # memb_sub_fee    = Column(MemSubKeys.memb_sub_fee, SmallInteger, nullable= False)

    # started_at      = Column(MemSubKeys.started_at, DateTime, nullable= False)
    cancelled_at    = Column(MemSubKeys.cancelled_at, DateTime, nullable= True)
    # expired_at      = Column(MemSubKeys.expired_at, DateTime, nullable= True)

    created_at      = Column(MemSubKeys.created_at, DateTime, default= current_time, nullable= False)
    updated_at      = Column(MemSubKeys.updated_at, DateTime, default= current_time, nullable= False)

    member_profile          = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._mem_sub)


class Languages(Base):
    __tablename__ = LanguageKeys.table_name

    id             = Column(LanguageKeys.id, SmallInteger,nullable=False, primary_key= True)
    name           = Column(LanguageKeys.name, String, nullable=False, unique=True)
    create_date    = Column(LanguageKeys.create_data, Date, default = current_time.date()  ,nullable= False)

    members        = relationship(MemberProfileKeys.py_table_name, secondary = member_language_association, back_populates=LanguageKeys._memb)
    
    
class InterestAreas(Base):
    __tablename__ = InterestAreaKeys.table_name

    id            = Column(InterestAreaKeys.id, SmallInteger,nullable=False, primary_key= True)
    name          = Column(InterestAreaKeys.name, String, nullable=False, unique=True)
    create_date    = Column(InterestAreaKeys.create_data, Date, default = current_time.date()  ,nullable= False)

    members       = relationship(MemberProfileKeys.py_table_name, secondary = member_interest_area_association, back_populates=InterestAreaKeys._memb)
    

class MemberStatus(Base):
    __tablename__ = MemberStatusKeys.table_name
    
    id            = Column(MemberStatusKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemberStatusKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    status        = Column(MemberStatusKeys.status, Integer, nullable= False, default= MemberStatusKeys.status_default)
    deleted_at    = Column(MemberStatusKeys.deleted_at, DateTime  ,nullable= True)
    banned_at     = Column(MemberStatusKeys.banned_at, DateTime  ,nullable= True)
    report_count  = Column(MemberStatusKeys.report_count, Integer, nullable= False, default = MemberStatusKeys.report_count_default)
    is_dating     = Column(MemberStatusKeys.is_dating, Boolean, nullable= False, default= MemberStatusKeys.is_dating_default)
    
    created_at    = Column(MemberStatusKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(MemberStatusKeys.updated_at, DateTime, default = current_time  ,nullable= False)

    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._mem_status)
    
    
    @validates("status")
    def validate_status(self, key, value):
        assert value in MemberStatusKeys.validate_status, f"Invalid status value: {value}"
        return value
    
    
class SignInSession(Base):
    __tablename__ = SignInKeys.table_name
    
    id            = Column(SignInKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(SignInKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    signin_id     = Column(SignInKeys.signin_id, String, nullable= False)
    type          = Column(SignInKeys.type, Integer, nullable= False)
    ip            = Column(SignInKeys.ip, String, nullable= True)
    device_type   = Column(SignInKeys.device_type, String, nullable= True)
    device_model  = Column(SignInKeys.device_model, String, nullable= True)
    signin_at     = Column(SignInKeys.signin_at, DateTime, default= current_time, nullable= False)
    signout_at    = Column(SignInKeys.signout_at, DateTime, default= None, nullable= True)

    created_at    = Column(SignInKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(SignInKeys.updated_at, DateTime, default = current_time  ,nullable= False)
    
    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._signin)


# class PromoOffer(Base):
#     __tablename__ = PromoOfferKeys.table_name
    
#     id            = Column(PromoOfferKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
#     member_id     = Column(PromoOfferKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= True)
#     type          = Column(PromoOfferKeys.type, String, nullable = False)
#     amount        = Column(PromoOfferKeys.amount, SmallInteger, nullable = False)
#     code          = Column(PromoOfferKeys.code, String, nullable = False, unique= True)
#     created_by    = Column(PromoOfferKeys.created_by, String, nullable= False, default= PromoOfferKeys.created_by_default)
#     effective_at  = Column(PromoOfferKeys.effective_at, DateTime, nullable= False)
#     redeemed_at   = Column(PromoOfferKeys.redeemed_at, DateTime, nullable= True)

#     created_at    = Column(PromoOfferKeys.created_at, DateTime, default= current_time, nullable= False)
#     updated_at    = Column(PromoOfferKeys.updated_at, DateTime, default= current_time, nullable= False)
    
#     member_sub    = relationship(MemSubKeys.py_table_name, uselist= False, back_populates=MemSubKeys._promo)
    
    

class Post(Base):
    __tablename__ = PostKeys.table_name
    id            = Column(PostKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(PostKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    ass_post_id   = Column(PostKeys.ass_post_id, UUID(as_uuid=True), ForeignKey(PostKeys.post_id_FK), nullable= True)

    intrst_id     = Column(PostKeys.intrst_id, SmallInteger, ForeignKey(InterestAreaKeys.int_id_FK), nullable= True)
    lang_id       = Column(PostKeys.lang_id, SmallInteger, ForeignKey(LanguageKeys.lang_id_FK), nullable= True)
    
    # is_anonymous  = Column(PostKeys.is_anonymous, Boolean, nullable= False, default= PostKeys.key_default)
    # is_drafted    = Column(PostKeys.is_drafted, Boolean, nullable= False, default= PostKeys.key_default)
    # is_blocked    = Column(PostKeys.is_blocked, Boolean, nullable= False, default= PostKeys.key_default)

    type          = Column(PostKeys.type, String, nullable= False)
    title         = Column(PostKeys.title, String, nullable= True)
    body          = Column(PostKeys.body, String, nullable= True)

    created_at    = Column(PostKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(PostKeys.updated_at, DateTime, default = current_time  ,nullable= False)

    member_profile      = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._member_posts)
    total_post_count    = relationship(MemTotalPostKeys.py_table_name, uselist= False, back_populates=MemTotalPostKeys._post)
    
    ass_post = relationship("Post", remote_side=[id], backref = backref(PostKeys._answers, cascade="all, delete-orphan"))

    # associated_post     = relationship(PostKeys.py_table_name, back_populates=PostKeys._parent_post)
    # parent_post         = relationship(PostKeys.py_table_name, back_populates=PostKeys._associated_post)


class MemFavReceived(Base):
    __tablename__ = MemFavRecKeys.table_name

    id            = Column(MemFavRecKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemFavRecKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK))
    fav_received  = Column(MemFavRecKeys.fav_received, SmallInteger, nullable = False, default= MemFavRecKeys.key_default)
    like_received = Column(MemFavRecKeys.like_received, SmallInteger, nullable = False, default= MemFavRecKeys.key_default)

    created_at    = Column(MemFavRecKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(MemFavRecKeys.updated_at, DateTime, default = current_time  ,nullable= False)
    
    member_profile = relationship(MemberProfileKeys.py_table_name,uselist= False, back_populates=MemberProfileKeys._fav_received)


class MemTotalPostCount(Base):
    __tablename__ = MemTotalPostKeys.table_name

    id            = Column(MemTotalPostKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemTotalPostKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK))

    post_count      = Column(MemTotalPostKeys.post_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    blog_count      = Column(MemTotalPostKeys.blog_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    question_count  = Column(MemTotalPostKeys.question_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    answer_count    = Column(MemTotalPostKeys.answer_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    poll_count      = Column(MemTotalPostKeys.poll_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)

    taken_poll_count  = Column(MemTotalPostKeys.taken_poll_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)

    draft_post_count  = Column(MemTotalPostKeys.draft_post_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    draft_blog_count  = Column(MemTotalPostKeys.draft_blog_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    draft_ques_count  = Column(MemTotalPostKeys.draft_ques_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    draft_ans_count   = Column(MemTotalPostKeys.draft_ans_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)
    draft_poll_count  = Column(MemTotalPostKeys.draft_poll_count, SmallInteger, nullable = False, default= MemTotalPostKeys.key_default)

    last_post_id            = Column(MemTotalPostKeys.last_post_id, UUID(as_uuid=True), ForeignKey(PostKeys.post_id_FK), nullable= True)
    last_post_lang          = Column(MemTotalPostKeys.last_post_lang, String, nullable= True)
    last_post_interest      = Column(MemTotalPostKeys.last_post_interest, String, nullable=False)

    created_at    = Column(MemTotalPostKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(MemTotalPostKeys.updated_at, DateTime, default = current_time  ,nullable= False)

    member_profile   = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._total_post_count)
    member_post      = relationship(PostKeys.py_table_name, back_populates=PostKeys._total_post_count)
   

class MemInvites(Base):
    __tablename__ = MemInvitesKeys.table_name

    id            = Column(MemInvitesKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemInvitesKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK))
    ques_invites  = Column(MemInvitesKeys.ques_invites, SmallInteger, nullable = False, default= MemInvitesKeys.key_default)
    poll_invites  = Column(MemInvitesKeys.poll_invites, SmallInteger, nullable = False, default= MemInvitesKeys.key_default)
    ques_invited  = Column(MemInvitesKeys.ques_invited, SmallInteger, nullable = False, default= MemInvitesKeys.key_default)
    poll_invited  = Column(MemInvitesKeys.poll_invited, SmallInteger, nullable = False, default= MemInvitesKeys.key_default)

    created_at    = Column(MemInvitesKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at    = Column(MemInvitesKeys.updated_at, DateTime, default = current_time  ,nullable= False)

    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._post_invites)


class MemAliasHist(Base):
    __tablename__ = MemAliasHistKeys.table_name
    
    id            = Column(MemAliasHistKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemAliasHistKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    
    alias         = Column(MemAliasHistKeys.alias, String(length=20), nullable=False)
    created_at    = Column(MemAliasHistKeys.created_at, DateTime, default = current_time, nullable= False)
    
    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._mem_alias_hist)
    
    
class AliasHist(Base):
    __tablename__ = AliasHistKeys.table_name
    
    id            = Column(AliasHistKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    alias         = Column(AliasHistKeys.alias, String(length=20), nullable=False, unique= True)
    
    created_at    = Column(AliasHistKeys.created_at, DateTime, default = current_time, nullable= False)
    