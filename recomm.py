from sqlalchemy import UUID, BigInteger, Column, Computed, DateTime, Integer, SmallInteger, String, Text, func, select, text
from sqlalchemy.orm import aliased

from database.table_keys import PostKeys, ViewMmbTagKeys
from utilities.constants import TableCharLimit

post_id = 'b309beea-a518-4d2e-bcb0-3ac922233fba'  

default_uuid7 = text("uuid_generate_v4()")
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import Computed, create_engine, Engine
from sqlalchemy.orm import sessionmaker, backref

from sqlalchemy.ext.declarative import declarative_base
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/2pm_test"
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


PostAlias = aliased(Post)
ViewMmbTagAlias = aliased(ViewMmbTag)

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
    select(tag_usage_subquery.c.member_id)
    .order_by(tag_usage_subquery.c.matching_tags.desc(), tag_usage_subquery.c.total_count.desc())
)




# Execute the query
with SessionLocal.begin() as session:

    recommended_users = session.execute(recommended_users_query).scalars().all()
    print(recommended_users)


print("done")