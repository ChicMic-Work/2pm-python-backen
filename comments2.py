from collections import OrderedDict
import datetime
from sqlalchemy import UUID, BigInteger, Boolean, Column, Computed, DateTime, Identity, Integer, PrimaryKeyConstraint, SmallInteger, String, Text, exists, func, select, text
from sqlalchemy.orm import aliased

from database.table_keys import CommentNodeKeys, CommentTreeKeys, MemberProfileKeys, PostKeys, QuesInvKeys, ViewMmbTagKeys

class TableCharLimit:
    post_title  = 70
    post_detail = 5000
    alias       = 20
    bio         = 150
    comment     = 300
    tag         = 25
    feedback    = 1000

    poll_qstn   = 150
    poll_choice = 70
    
    _255        = 255
    _330        = 330


default_uuid7 = text("mbr.uuid_generate_v4()")
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import Computed, create_engine, Engine
from sqlalchemy.orm import sessionmaker, backref, Session

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





class CommentNode(Base):
    
    __tablename__ = "comments"
    __table_args__  = {'schema': CommentNodeKeys.schema_clb}
    
    id      = Column( UUID(as_uuid=True),nullable=False, primary_key= True, server_default = default_uuid7)
    post_id         = Column(UUID(as_uuid=True), nullable= False)
    parent_id       = Column( UUID(as_uuid=True), nullable=True)
    content            = Column( Text, nullable=False)
    created_at       = Column(DateTime())
    

class CommentTree(Base):
    
    __tablename__ = "comments_closure"
    __table_args__  = (
        PrimaryKeyConstraint("ancestor", "descendant", "depth"),
        {'schema': CommentTreeKeys.schema_clb},
    )
    
    ancestor     = Column(UUID(as_uuid=True), nullable= False)
    descendant      = Column( UUID(as_uuid=True), nullable= False)
    depth         = Column(SmallInteger, nullable=False)


n = 1 # outer limit

c = 1 # inner limit

d = 2 # depth

offset = 0 # Initial Comments

inital_inner_offset = 0

post_id = "b2555719-bc51-49bb-a335-0827a692325d"

_outer = (
    select(CommentNode)
    .where(
        CommentNode.post_id == post_id,
        CommentNode.parent_id == None
    )
    .order_by(CommentNode.created_at.asc())
    .limit(n)
)




# Outer Load More count
def get_load_more_count_root(post_id, offset, limit, ses: Session):

    exclude_parent_query = (
        select(CommentNode.id)
        .where(
            CommentNode.post_id == post_id,
            CommentNode.parent_id == None
        )
        .order_by(CommentNode.created_at.asc())
        .limit(offset + limit)
    )

    exclude_parent_ids = ses.execute(exclude_parent_query).scalars().all()

    exclude_all_query = (
        select(CommentTree.descendant)
        .where(
            CommentTree.ancestor.in_(exclude_parent_ids)
        )
    )

    exclude_all_ids = ses.execute(exclude_all_query).scalars().all()

    count_query = (
        select(func.count())
        .select_from(CommentTree)
        .join(CommentNode, CommentNode.id == CommentTree.ancestor)
        .where(
            CommentTree.ancestor.not_in(exclude_all_ids),
            CommentNode.post_id == post_id
        )
    )

    count = ses.execute(count_query).scalars().one_or_none()
    if count == None:
        count = 0

    return count


def get_load_more_count_inner(comment_id: UUID, inner_offset, inner_limit, ses: Session):

    include_comment_query = (
        select(CommentNode.id)
        .where(
            CommentNode.parent_id == comment_id
        )
        .order_by(CommentNode.created_at.asc())
        .offset(inner_limit + inner_offset)
    )

    include_comment_ids = ses.execute(include_comment_query).scalars().all()

    count_query = (
        select(func.count())
        .select_from(CommentTree)
        .where(CommentTree.ancestor.in_(include_comment_ids))
    )

    count = ses.execute(count_query).scalars().one_or_none()

    return count if count else 0



def get_load_more_count_depth(comment_id, ses: Session):

    count_query = (
        select(func.count())
        .select_from(CommentTree)
        .where(
            CommentTree.ancestor == comment_id,
            CommentTree.depth > 0
        )
    )

    count = ses.execute(count_query).scalars().one_or_none()

    return count if count else 0


# Get Child Vertical with Limit
def get_child_cmnts(parent_id, inner_limit, inner_offset, ses: Session):

    _inner = (
        select(CommentNode)
        .where(
            CommentNode.parent_id == parent_id
        )
        .order_by(CommentNode.created_at.asc())
        .offset(inner_offset)
        .limit(inner_limit)
        
    )


    _inner_list = ses.execute(_inner).scalars().all()
    print(_inner_list)
    return _inner_list




def get_root_comment_dict(ses: Session, cmnt_id, depth, inner_offset, inner_limit):

    def fetch_replies(comment_id, current_depth, inner_offset):
        if current_depth > depth:
            return [{"load_more": get_load_more_count_depth(comment_id, ses)}]
        child_comments = get_child_cmnts(comment_id, inner_limit, inner_offset, ses)
        replies = []
        if child_comments:
            for child in child_comments:
                child_dict = {
                    "id": child.id,
                    "text": child.content,
                    "root_id": child.id,
                    "created_at": child.created_at,
                    "replies": fetch_replies(child.id, current_depth + 1, inner_offset = 0)
                }
                replies.append(child_dict)
            if current_depth <= depth:
                replies.append({"load_more": get_load_more_count_inner(comment_id, inner_offset, inner_limit, ses)})
        else:
            replies.append({"load_more": 0})
        return replies
    
    root_comment = ses.execute(select(CommentNode).where(CommentNode.id == cmnt_id)).scalar_one()
    root_dict = {
        "id": root_comment.id,
        "text": root_comment.content,
        "root_id": root_comment.id,
        "created_at": root_comment.created_at,
        "replies": fetch_replies(cmnt_id, 1, inner_offset)
    }

    return root_dict

        
with SessionLocal.begin() as session:
    _outer_list = []

    for row in session.execute(_outer).fetchall():
        _outer_list.append(
            row[0]
        )

    comments_list = []

    for cmnt in _outer_list:
        comment_dict = {
            "id": cmnt.id,
            "text": cmnt.content,
            "root_id": cmnt.id,
            "created_at": cmnt.created_at,
            "replies": []
        }
        comment_dict["replies"] = get_root_comment_dict(session, cmnt.id, d, inital_inner_offset, c)["replies"]
        comments_list.append(comment_dict)

    comments_list.append({"load_more": get_load_more_count_root(post_id, offset, n, session)})

print(f"NORMAL ROOT COMMENTS -> n = {n}, c = {c}, d = {d} ")
print(comments_list)





    
"""
    how do i implement recursive depth function
    comments_list should look like this -

    [
        {
        "id": id,
        "text": child.content,
        "root_id": root_id,
        "created_at": created_at,
        "replies": [
                    {
                    "id": id,
                    "text": child.content,
                    "root_id": root_id,
                    "created_at": created_at,
                    "replies": [
                                {
                                "id": id,
                                "text": child.content,
                                "root_id": root_id,
                                "created_at": created_at,
                                "replies": [],
                                },
                                {
                                    "load_more": int
                                }
                            ]
                    },
                    {
                        "load_more": int
                    }
                ]
        },
        {
            "load_more": int #could be 0
        }
    ]
    
"""
id = ''
content = ''
root_id = ''
created_at = ''
[
        {
        "id": id,
        "text": content,
        "root_id": root_id,
        "created_at": created_at,
        "replies": [
                    {
                    "id": id,
                    "text": content,
                    "root_id": root_id,
                    "created_at": created_at,
                    "replies": [
                                {
                                "id": id,
                                "text": content,
                                "root_id": root_id,
                                "created_at": created_at,
                                "replies": [
                                    # Depth 2 reached here, so show load_more
                                    {"load_more": int}
                                ],
                                },
                                {
                                    "load_more": int
                                }
                            ]
                    },
                    # inner limit (c) 1 reached here, so show load_more 
                    {
                        "load_more": int
                    }
                ]
        },
        # outer limit (n) 1 reached here, so show load_more 
        {
            "load_more": int #could be 0
        }
    ]




#FIRST TRY, n = 1, c = 1, d = 2
[
    {
    'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'text': '01',
    'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
    'replies': [
                {
                'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                'text': '01.01',
                'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                'created_at': datetime.datetime(2024, 6, 29, 16, 4, 22, 394428),
                'replies': [
                            {
                            'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                            'text': '01.01.01',
                            'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                            'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
                            'replies': [
                                        {
                                            'load_more': 3 #2
                                        }
                                    ]
                            }, 
                            {
                                'load_more': 3
                            }
                        ]
                }, 
                {
                    'load_more': 3 #5
                }
            ]
    }, 
    {
        'load_more': 3
    }
]


#Load depth, n = 1, c = 1, d = 2
[
    {
        'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
        'text': '01',
        'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
        'replies': [
                    {
                    'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                    'text': '01.01',
                    'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                    'created_at': datetime.datetime(2024, 6, 29, 16, 4, 22, 394428),
                    'replies': [
                                {
                                'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                                'text': '01.01.01',
                                'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                                'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
                                'replies': [{
                                        'load_more': 2
                                    }]
                                }, 
                                {
                                    'load_more': 3
                                }
                            ]
                    }, 
                    {
                        'load_more': 3
                    }
                ]
    }, 
    {
    'load_more': 3
    }
]


# load + inner - n=1, c=1, d=2
[
{
    'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'text': '01',
    'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
    'replies': [
    {
        'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'text': '01.01',
        'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'created_at': datetime.datetime(2024, 6,
            29, 16, 4, 22, 394428),
        'replies': [
        {
            'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'text': '01.01.01',
            'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
            'replies': [
            {
                'load_more': 2
            }]
        },
        {
            'load_more': 3
        }]
    },
    {
        'load_more': 5
    }]
},
{
    'load_more': 3
}]
# n = 2, c = 2, d= 2

[
    {
    'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'text': '01',
    'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
    'replies': [
                {
                'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                'text': '01.01',
                'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
                'created_at': datetime.datetime(2024, 6, 29, 16, 4, 22, 394428),
                'replies': [
                            {
                                'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                                'text': '01.01.01',
                                'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
                                'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
                                'replies': [{
                                    'load_more': 3 #2
                                }]
                            }, 
                            {
                                'id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
                                'text': '01.01.02',
                                'root_id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
                                'created_at': datetime.datetime(2024, 6, 29, 16, 30, 0, 830663),
                                'replies': [{
                                    'load_more': 3 #0
                                }]
                            }, 
                            {
                                'load_more': 3 #2
                            }
                        ]
                }, 
                {
                'id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
                'text': '01.02',
                'root_id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
                'created_at': datetime.datetime(2024, 6, 29, 16, 26, 4, 958909),
                'replies': [
                            {
                                'id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
                                'text': '01.02.01',
                                'root_id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
                                'created_at': datetime.datetime(2024, 6, 29, 16, 30, 57, 939623),
                                'replies': [{
                                    'load_more': 3 #0
                                }]
                            }, 
                            {
                                'id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
                                'text': '01.02.02',
                                'root_id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
                                'created_at': datetime.datetime(2024, 6, 29, 16, 31, 2, 355341),
                                'replies': [{
                                    'load_more': 3 #0
                                }]
                            }, 
                            {
                                'load_more': 3 #1
                            }]
                }, 
                {
                'load_more': 3 #1

                }
            ]
    }, 
    {
        'id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
        'text': '02',
        'root_id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 27, 30, 179230),
        'replies': [{
            'load_more': 39 #0
        }]
    }, 
    {
        'load_more': 2
    }
]



# Load Depth n = 2, c = 2, d= 2
[
{
    'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'text': '01',
    'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
    'replies': [
    {
        'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'text': '01.01',
        'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 4, 22, 394428),
        'replies': [
        {
            'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'text': '01.01.01',
            'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
            'replies': [
            {
                'load_more': 2
            }]
        },
        {
            'id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
            'text': '01.01.02',
            'root_id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 30, 0, 830663),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'load_more': 3
        }]
    },
    {
        'id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
        'text': '01.02',
        'root_id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 26, 4, 958909),
        'replies': [
        {
            'id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
            'text': '01.02.01',
            'root_id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 30, 57, 939623),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
            'text': '01.02.02',
            'root_id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 31, 2, 355341),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'load_more': 3
        }]
    },
    {
        'load_more': 3
    }]
},
{
    'id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
    'text': '02',
    'root_id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 27, 30, 179230),
    'replies': [
    {
        'load_more': 39
    }]
},
{
    'load_more': 2
}]



# depth + inner 
[
{
    'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'text': '01',
    'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
    'replies': [
    {
        'id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'text': '01.01',
        'root_id': UUID('14756fc9-540e-429b-ad2a-e01d41034840'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 4, 22, 394428),
        'replies': [
        {
            'id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'text': '01.01.01',
            'root_id': UUID('30b8c47b-3dce-46c2-853c-f4b19bca839a'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 5, 35, 956516),
            'replies': [
            {
                'load_more': 2
            }]
        },
        {
            'id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
            'text': '01.01.02',
            'root_id': UUID('5138f428-3ff8-4b08-9c0a-a337504dfb3d'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 30, 0, 830663),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'load_more': 2
        }]
    },
    {
        'id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
        'text': '01.02',
        'root_id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 26, 4, 958909),
        'replies': [
        {
            'id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
            'text': '01.02.01',
            'root_id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 30, 57, 939623),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
            'text': '01.02.02',
            'root_id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
            'created_at': datetime.datetime(2024, 6, 29, 16, 31, 2, 355341),
            'replies': [
            {
                'load_more': 0
            }]
        },
        {
            'load_more': 1
        }]
    },
    {
        'load_more': 1
    }]
},
{
    'id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
    'text': '02',
    'root_id': UUID('dcd1543e-2276-4919-bba7-f6c8f529f1f5'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 27, 30, 179230),
    'replies': [
    {
        'load_more': 0
    }]
},
{
    'load_more': 2
}]


# When Fetching load more on Root comments
with SessionLocal.begin() as session:

    _root_offset = 1

    _inner_offset = 0

    root_offset_query = (
        select(CommentNode)
        .where(CommentNode.post_id == post_id,
               CommentNode.parent_id == None)
        .order_by(CommentNode.created_at.asc())
        .offset(_root_offset)
        .limit(n)
    )

    _outer_list_root_offset = []

    for row in session.execute(root_offset_query).fetchall():
        _outer_list_root_offset.append(
            row[0]
        )

    root_offset_comments_list = []

    for cmnt in _outer_list_root_offset:
        comment_dict = {
            "id": cmnt.id,
            "text": cmnt.content,
            "root_id": cmnt.id,
            "created_at": cmnt.created_at,
            "replies": []
        }
        comment_dict["replies"] = get_root_comment_dict(session, cmnt.id, d, _inner_offset, c)["replies"]
        root_offset_comments_list.append(comment_dict)

    root_offset_comments_list.append({"load_more": get_load_more_count_root(post_id, _root_offset, n, session)})


print(f"ROOT WITH OFFSET COMMENTS -> n = {n}, c = {c}, d = {d}, _root_offset = {_root_offset}, _inner_offset = {_inner_offset} ")
print(root_offset_comments_list)


with SessionLocal.begin() as session:

    cmnt_id = '05332767-73c6-4f61-9e3e-92587a473892'

    _inner_offset = 1

    comment_query = (
        select(CommentNode)
        .where(CommentNode.id == cmnt_id)
    )

    cmnt = session.get(CommentNode, cmnt_id)

    inner_cmnt_offset_list = []

    comment_dict = {
        "id": cmnt.id,
        "text": cmnt.content,
        "root_id": cmnt.id,
        "created_at": cmnt.created_at,
        "replies": []
    }
    c = 2
    d = 10
    comment_dict["replies"] = get_root_comment_dict(session, cmnt.id, d, _inner_offset, c)["replies"]

    inner_cmnt_offset_list.append(comment_dict)

print(f"INNER WITH OFFSET COMMENTS -> n = {n}, c = {c}, d = {d}, _inner_offset = {_inner_offset} ")
print(inner_cmnt_offset_list)



# INNER WITH OFFSET COMMENTS -> n = 1, c = 1, d = 2, _inner_offset = 1
[
    {
        'id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
        'text': '01',
        'root_id': UUID('6f91cd7e-0edb-438d-a087-813c6d8862d3'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 2, 11, 383316),
        'replies': [
                    {
                        'id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
                        'text': '01.02',
                        'root_id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
                        'created_at': datetime.datetime(2024, 6,
                            29, 16, 26, 4, 958909),
                        'replies': [
                                    {
                                        'id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
                                        'text': '01.02.01',
                                        'root_id': UUID('8dfe0cf0-6ca0-4ae5-b778-33745b81a070'),
                                        'created_at': datetime.datetime(2024, 6, 29, 16, 30, 57, 939623),
                                        'replies': [
                                                {
                                                    'load_more': 0
                                                }
                                        ]
                                    },
                                    {
                                        'load_more': 2
                                    }
                                ]
                    },
                    {
                        'load_more': 1
                    }
        ]
    }
]



# INNER WITH OFFSET COMMENTS -> n = 1, c = 2, d = 10, _inner_offset = 1
[
{
    'id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
    'text': '01.02',
    'root_id': UUID('05332767-73c6-4f61-9e3e-92587a473892'),
    'created_at': datetime.datetime(2024, 6, 29, 16, 26, 4, 958909),
    'replies': [
    {
        'id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
        'text': '01.02.02',
        'root_id': UUID('c6580e29-342b-46b0-8092-1b6bb67a1f11'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 31, 2, 355341),
        'replies': [
        {
            'load_more': 0
        }]
    },
    {
        'id': UUID('806750af-7e43-4cd3-9840-7aa9f0307d73'),
        'text': '01.02.03',
        'root_id': UUID('806750af-7e43-4cd3-9840-7aa9f0307d73'),
        'created_at': datetime.datetime(2024, 6, 29, 16, 31, 4, 637257),
        'replies': [
        {
            'load_more': 0
        }]
    },
    {
        'load_more': 0
    }]
}]