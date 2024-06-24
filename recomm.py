from sqlalchemy import UUID, BigInteger, Boolean, Column, Computed, DateTime, Identity, Integer, SmallInteger, String, Text, exists, func, select, text
from sqlalchemy.orm import aliased

from database.table_keys import MemberProfileKeys, PostKeys, QuesInvKeys, ViewMmbTagKeys
from utilities.constants import TableCharLimit



default_uuid7 = text("uuid_generate_v7()")
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import Computed, create_engine, Engine
from sqlalchemy.orm import sessionmaker, backref

from sqlalchemy.ext.declarative import declarative_base
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@postgres:5432/2pm_test"
# engine = create_async_engine(SQLALCHEMY_DATABASE_URL,)
# SessionLocal = async_sessionmaker(bind= engine, autocommit=False, autoflush=False, class_= AsyncSession )
engine = create_engine(SQLALCHEMY_DATABASE_URL,)
SessionLocal = sessionmaker(bind= engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Post(Base):
    __tablename__ = PostKeys.table_name
    __table_args__  = {'schema': PostKeys.schema_pst}
    
    id            = Column(PostKeys.id, UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    member_id     = Column(PostKeys.member_id, UUID(as_uuid=True), nullable= False, index= True)
    
    type          = Column(PostKeys.type, String(TableCharLimit._255), nullable= False)
    assc_post_id  = Column(PostKeys.assc_post_id, UUID(as_uuid=True), nullable= True)

    interest_id   = Column(PostKeys.interest_id, SmallInteger, nullable= True)
    lang_id       = Column(PostKeys.lang_id, SmallInteger, nullable= True)
    
    title         = Column(PostKeys.title, String(TableCharLimit._255), nullable= False)
    body          = Column(PostKeys.body, Text, nullable= False)

    tag1          = Column(PostKeys.tag1, String(TableCharLimit._255), nullable= False)
    tag2          = Column(PostKeys.tag2, String(TableCharLimit._255), nullable= True)
    tag3          = Column(PostKeys.tag3, String(TableCharLimit._255), nullable= True)

    tag1_std = Column(PostKeys.tag1_std,String(TableCharLimit._255),Computed("mbr.normalize_tag(tag1)", persisted = True), nullable=False)
    tag2_std = Column(PostKeys.tag2_std,String(TableCharLimit._255),Computed("mbr.normalize_tag(tag2)", persisted=True), nullable=True)
    tag3_std = Column(PostKeys.tag3_std,String(TableCharLimit._255),Computed("mbr.normalize_tag(tag3)", persisted=True), nullable=True)

    post_at       = Column(PostKeys.posted_at, DateTime(True), default= func.now())


class ViewMmbTag(Base):
    
    __tablename__   = ViewMmbTagKeys.tablename
    __table_args__  = {'schema': ViewMmbTagKeys.schema_pst}
    
    id              = Column(ViewMmbTagKeys.ID, BigInteger, primary_key= True)
    member_id       = Column(ViewMmbTagKeys.member_id, UUID(as_uuid=True), nullable= False)
    
    tag_std         = Column(ViewMmbTagKeys.tag_std, String(TableCharLimit._255), nullable=False)
    count           = Column(ViewMmbTagKeys.count, Integer, nullable=False)
    
    first_at        = Column(ViewMmbTagKeys.fst_at, DateTime(True), nullable=False)
    last_at         = Column(ViewMmbTagKeys.lst_at, DateTime(True), nullable=False)
    
    create_at       = Column(ViewMmbTagKeys.create_at, DateTime(True),nullable=False)

class MemberProfileCurr(Base):
    
    __tablename__   = MemberProfileKeys.table_name_curr
    __table_args__ = {'schema': MemberProfileKeys.schema_mbr}
    
    id              = Column(MemberProfileKeys.id , UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    apple_id        = Column(MemberProfileKeys.apple_id, String(TableCharLimit._255), nullable= True)
    apple_email     = Column(MemberProfileKeys.apple_email, String(TableCharLimit._330), nullable= True)
    google_id       = Column(MemberProfileKeys.google_id, String(TableCharLimit._255), nullable= True)
    google_email    = Column(MemberProfileKeys.google_email, String(TableCharLimit._330), nullable= True)
    join_at         = Column(MemberProfileKeys.join_at, DateTime(timezone= True), default= func.now(), nullable= False)
    
    alias           = Column(MemberProfileKeys.alias, String(TableCharLimit._255))
    alias_std       = Column(MemberProfileKeys.alias_std, String(TableCharLimit._255))
    
    bio             = Column(MemberProfileKeys.bio, String(TableCharLimit._255), nullable= True)
    image           = Column(MemberProfileKeys.image, String(TableCharLimit._255), nullable= True)
    gender          = Column(MemberProfileKeys.gender, String(TableCharLimit._255))
    is_dating       = Column(MemberProfileKeys.is_dating, Boolean, default=MemberProfileKeys.is_dating_default)
    
    
    update_at       = Column(MemberProfileKeys.update_at, DateTime(timezone= True))

class QuesInvite(Base):
    
    __tablename__   = QuesInvKeys.tablename
    __table_args__  = {'schema': QuesInvKeys.schema_pst}
    
    id              = Column(QuesInvKeys.ID, BigInteger, Identity(always=True), primary_key= True)
    
    ques_post_id    = Column(QuesInvKeys.ques_post_id, UUID(as_uuid=True))
    ans_post_id     = Column(QuesInvKeys.ans_post_id, UUID(as_uuid=True), nullable= True)
    
    invite_at       = Column(QuesInvKeys.invite_at, DateTime(True), default= func.now())
    
    inviting_mbr_id = Column(QuesInvKeys.inviting_mbr_id, UUID(as_uuid=True), nullable=False)
    invited_mbr_id  = Column(QuesInvKeys.invited_mbr_id, UUID(as_uuid=True), nullable=False)


PostAlias = aliased(Post)
ViewMmbTagAlias = aliased(ViewMmbTag)
post_id = '06672e03-4cac-719b-8000-13d03c4bcdf0'  

invited_subquery = (
    select(QuesInvite.invited_mbr_id)
    .where(QuesInvite.ques_post_id == post_id,
           QuesInvite.inviting_mbr_id == '06672c49-868c-78a2-8000-a0e843d9b8e9')
    .subquery()
)

# Subquery to get the tags and post creator
post_tags_subquery = (
    select(
        PostAlias.tag1_std,
        PostAlias.tag2_std,
        PostAlias.tag3_std,
        PostAlias.member_id.label('post_creator')
    )
    .where(PostAlias.id == post_id)
    .subquery()
)

# Subquery to get tag usage
tag_usage_subquery = (
    select(
        ViewMmbTagAlias.member_id,
        func.count(ViewMmbTagAlias.tag_std).label('matching_tags'),
        func.sum(ViewMmbTagAlias.count).label('total_count')
    )
    .join(post_tags_subquery, ViewMmbTagAlias.tag_std.in_([
        post_tags_subquery.c.tag1_std,
        post_tags_subquery.c.tag2_std,
        post_tags_subquery.c.tag3_std
    ]))
    .where(ViewMmbTagAlias.member_id != post_tags_subquery.c.post_creator)
    .group_by(ViewMmbTagAlias.member_id)
    .subquery()
)

# Final query to get recommended users
recommended_users_query = (
    select(tag_usage_subquery.c.member_id,
            MemberProfileCurr.alias,
            MemberProfileCurr.image,
            MemberProfileCurr.bio,
            exists(invited_subquery.c.invited_mbr_id)
                .where(invited_subquery.c.invited_mbr_id == tag_usage_subquery.c.member_id)
                .label("invited_already")
    )
    # .join(tag_usage_subquery, tag_usage_subquery.c.member_id == MemberProfileCurr.id)
    .join(MemberProfileCurr, tag_usage_subquery.c.member_id == MemberProfileCurr.id)
    .order_by(tag_usage_subquery.c.matching_tags.desc(), tag_usage_subquery.c.total_count.desc())
)




# Execute the query
with SessionLocal.begin() as session:

    recommended_users = session.execute(recommended_users_query).fetchall()
    print(recommended_users)


print("done")