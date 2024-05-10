from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    )

from database.table_keys import (
    MemberProfileKeys, MmbLangKeys,
    LanguageKeys, MmbIntAreaKeys,
    InterestAreaKeys, MemberStatusKeys,
    SignInKeys, PromoOfferKeys 
)

from sqlalchemy.orm import validates, relationship

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:1234@postgres:5432/2pm_test"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,)
SessionLocal = async_sessionmaker(bind= engine, autocommit=False, autoflush=False, class_= AsyncSession )

Base = declarative_base()

default_uuid7 = text("uuid_generate_v7()")

member_language_association = Table(
    MmbLangKeys.table_name,
    Base.metadata,
    Column(MmbLangKeys.id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK)),
    Column(MmbLangKeys.language_id, UUID(as_uuid=True), ForeignKey(LanguageKeys.lang_id_FK)),
)

member_interest_area_association = Table(
    MmbIntAreaKeys.table_name,
    Base.metadata,
    Column(MmbIntAreaKeys.id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK)),
    Column(MmbIntAreaKeys.int_area_id, UUID(as_uuid=True), ForeignKey(InterestAreaKeys.int_id_FK)),
)

class MemberProfile(Base):
    __tablename__   = MemberProfileKeys.table_name
    id              = Column(MemberProfileKeys.id , UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    apple_id        = Column(MemberProfileKeys.apple_id, String, unique=True, index=True)
    google_id       = Column(MemberProfileKeys.google_id, String, unique=True, index=True)
    alias           = Column(MemberProfileKeys.alias, String, unique=True, index=True)
    bio             = Column(MemberProfileKeys.bio, String)
    image           = Column(MemberProfileKeys.image, String)
    gender          = Column(MemberProfileKeys.gender, String)
    created_at      = Column(MemberProfileKeys.created_at, DateTime, default = current_time  ,nullable= False)
    updated_at      = Column(MemberProfileKeys.updated_at, DateTime, default = current_time  ,nullable= False)
    
    language_choices        = relationship(LanguageKeys.py_table_name, secondary = member_language_association, back_populates= MemberProfileKeys._lang)
    interest_area_choices   = relationship(InterestAreaKeys.py_table_name, secondary = member_interest_area_association, back_populates= MemberProfileKeys._int_area)
    
    status                  = relationship(MemberStatusKeys.py_table_name, uselist=False, back_populates=MemberStatusKeys._memb)
    session                 = relationship(SignInKeys.py_table_name, back_populates=SignInKeys._memb)
    
    promo_offers            = relationship(PromoOfferKeys.py_table_name, back_populates=PromoOfferKeys._memb)
    
    @validates("gender")
    def validate_gender(self, key, value):
        assert value in MemberProfileKeys.gender_validation, f"Invalid gender: {value}"
        return value
    
Index('ix_apple_id_unique', MemberProfile.apple_id, unique=True, postgresql_where=MemberProfile.apple_id.isnot(None))
Index('ix_alias_unique', MemberProfile.alias, unique=True, postgresql_where=MemberProfile.alias.isnot(None))
Index('ix_google_id_unique', MemberProfile.google_id, unique=True, postgresql_where=MemberProfile.google_id.isnot(None))
    
    # __table_args__ = (
    #     CheckConstraint(
    #         f"({MemberProfileKeys.apple_id.lower()} IS NULL AND {MemberProfileKeys.google_id.lower()} IS NOT NULL) OR ({MemberProfileKeys.apple_id.lower()} IS NOT NULL AND {MemberProfileKeys.google_id.lower()} IS NULL)",
    #         name="chk_either_apple_or_google_id_null"
    #     ),
    # )
    
    # __table_args__ = (
    #     CheckConstraint(
    #         f"(({MemberProfileKeys.column_with_tn(MemberProfileKeys.apple_id)}) IS NULL AND ({MemberProfileKeys.column_with_tn(MemberProfileKeys.google_id)}) IS NOT NULL) OR (({MemberProfileKeys.column_with_tn(MemberProfileKeys.apple_id)}) IS NOT NULL AND ({MemberProfileKeys.column_with_tn(MemberProfileKeys.google_id)}) IS NULL)",
    #         name="chk_either_apple_or_google_id_null"
    #     ),
    # )
    
    
class Languages(Base):
    __tablename__ = LanguageKeys.table_name

    id             = Column(LanguageKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    name           = Column(LanguageKeys.name, String, nullable=False, unique=True)
    created_at     = Column(MemberProfileKeys.created_at, DateTime, default = current_time  ,nullable= False)

    members        = relationship(MemberProfileKeys.py_table_name, secondary = member_language_association, back_populates=LanguageKeys._memb)
    
    
class InterestAreas(Base):
    __tablename__ = InterestAreaKeys.table_name

    id            = Column(InterestAreaKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    name          = Column(InterestAreaKeys.name, String, nullable=False, unique=True)
    created_at    = Column(InterestAreaKeys.created_at, DateTime, default = current_time  ,nullable= False)

    members       = relationship(MemberProfileKeys.py_table_name, secondary = member_interest_area_association, back_populates=InterestAreaKeys._memb)
    

class MemberStatus(Base):
    __tablename__ = MemberStatusKeys.table_name
    
    id            = Column(MemberStatusKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(MemberStatusKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= False)
    status        = Column(MemberStatusKeys.status, Integer, nullable= False, default= MemberStatusKeys.status_default)
    deleted_at    = Column(MemberStatusKeys.deleted_at, DateTime  ,nullable= True)
    banned_at     = Column(MemberStatusKeys.banned_at, DateTime  ,nullable= True)
    report_count  = Column(MemberStatusKeys.report_count, Integer, nullable= False, default = MemberStatusKeys.report_count_default)
    is_dating     = Column(MemberStatusKeys.is_dating, Integer, nullable= False, default= MemberStatusKeys.is_dating_default)
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
    
    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._signin)


class PromoOffer(Base):
    __tablename__ = PromoOfferKeys.table_name
    
    id            = Column(PromoOfferKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(PromoOfferKeys.member_id, UUID(as_uuid=True), ForeignKey(MemberProfileKeys.mem_id_FK), nullable= True)
    type          = Column(PromoOfferKeys.type, String, nullable = False)
    amount        = Column(PromoOfferKeys.amount, SmallInteger, nullable = False)
    code          = Column(PromoOfferKeys.code, String, nullable = False, unique= True)
    created_by    = Column(PromoOfferKeys.created_by, String, nullable= False, default= PromoOfferKeys.created_by_default)
    effective_at  = Column(PromoOfferKeys.effective_at, DateTime, nullable= False)
    redeemed_at   = Column(PromoOfferKeys.redeemed_at, DateTime, nullable= True)
    created_at    = Column(PromoOfferKeys.created_at, DateTime, default= current_time, nullable= False)
    updated_at    = Column(PromoOfferKeys.updated_at, DateTime, default= current_time, nullable= False)
    
    member_profile = relationship(MemberProfileKeys.py_table_name, back_populates=MemberProfileKeys._promo)
    
    