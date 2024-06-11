import random
from sqlalchemy import select, asc, delete, desc, func, and_, or_, text
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from schemas.s_posts import PostAnsResponse, PostBlogQuesResponse, PostPollResponse
from utilities.constants import (
    AddType, ChoicesType, PaginationLimit, PostType, current_datetime
)

from datetime import datetime, timedelta

from database.models import (
    DailyAns, DailyQues, MemberProfileCurr, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist, ViewPostScore
)
from uuid_extensions import uuid7

from crud.c_posts import (
    get_poll_post_items
)

def get_post_tags_list(post: Post) -> List[str]:

    tags = []
    if post.tag1:
        tags.append(post.tag1)
    if post.tag2:
        tags.append(post.tag2)
    if post.tag3:
        tags.append(post.tag3)

    return tags


def get_member_dict_for_post_detail(
    post_curr: PostStatusCurr,
    user: MemberProfileCurr = None,
    image: str = None,
    alias: str = None,
):
    member = {
            "image": user.image if user else image,
            "alias": user.alias if user else alias,
            "is_anonymous": post_curr.is_anonymous
        }
    if post_curr.is_anonymous:
        member["alias"] = "Anonymous"
        member["image"] = None
        member["is_anonymous"] = post_curr.is_anonymous
    
    return member




## DRAFTS ##
#BLOG
async def get_blog_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    blogs = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Blog).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return blogs


#QUES
async def get_ques_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    questions = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Question).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return questions


#ANS
async def get_ans_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    answers = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Answer).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    return answers


#POLL
async def get_poll_drafts(
    db: AsyncSession,
    mem_id: UUID
) -> List[PostDraft]:
    
    polls = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == PostType.Poll).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    for poll in polls:
        poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == poll.id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
        poll.body = poll_ques.ques_text
    
    return polls



## ANSWER A QUESTION ##

async def get_post_questions_list(
    db: AsyncSession,
    member_id: UUID,
    limit: int,
    offset: int
) -> List[Tuple[Post, PostStatusCurr, str, str]]:
    
    answered_post_ids_query = (
        select(Post.assc_post_id)
        .where(
            Post.member_id == member_id,
            Post.type == PostType.Answer,
        )
    ).alias("answered_posts")
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.type == PostType.Question,
            Post.id.notin_(answered_post_ids_query),
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    questions = results.fetchall()
    
    return questions


"""
async def get_post_questions(db: AsyncSession, limit: int = 10, offset: int = 0) -> List[Dict]:
    # First query to get posts and their status
    query = (
        select(Post, PostStatusCurr)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .where(
            Post.type == 'Question',
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    posts_and_statuses = results.fetchall()
    
    post_ids = [post.id for post, status in posts_and_statuses if not status.is_anonymous]

    # Conditionally fetch member details
    if post_ids:
        member_query = (
            select(Post.id, MemberProfileCurr.image, MemberProfileCurr.alias)
            .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
            .where(Post.id.in_(post_ids))
        )
        member_results = await db.execute(member_query)
        member_details = {result[0]: {"image": result[1], "alias": result[2]} for result in member_results.fetchall()}
    else:
        member_details = {}

    return [
        {
            "post": post,
            "status": {
                "is_anonymous": status.is_anonymous,
                "is_deleted": status.is_deleted,
                "is_blocked": status.is_blocked,
                "update_at": status.update_at
            },
            "member": member_details.get(post.id, {"image": None, "alias": None}) if not status.is_anonymous else {"image": None, "alias": None}
        }
        for post, status in posts_and_statuses
    ]
"""


async def get_post_question(
    db: AsyncSession,
    post_id: UUID,
    limit: int ,
    offset: int
) -> Tuple[Tuple[Post, PostStatusCurr, str, str], List[Tuple[Post, PostStatusCurr, str, str]]]:
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(Post.id == post_id)
    )
    results = await db.execute(query)
    post = results.fetchone()
    
    if not post:
        raise Exception("Post not found")
    if post[1].is_deleted:
        raise Exception("Post is deleted") 
    if post[1].is_blocked:
        raise Exception("Post is blocked")
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.assc_post_id == post_id
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    results = await db.execute(query)
    answers = results.fetchall()
    
    return post, answers



## TAKE A POLL ##
async def get_post_polls_list(
    db: AsyncSession,
    member_id: UUID,
    limit: int,
    offset: int
):
    taken_post_ids_query = (
        select(PollMemTake.post_id)
        .where(
            PollMemTake.member_id == member_id,
        )
    ).alias("poll_taken")
    
    revealed_post_ids_query = (
        select(PollMemReveal.post_id)
        .where(
            PollMemReveal.member_id == member_id,
        )
    ).alias("poll_revealed")
    
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.type == PostType.Poll,
            Post.id.notin_(taken_post_ids_query),
            Post.id.notin_(revealed_post_ids_query),
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .order_by(desc(Post.post_at))
        .limit(limit)
        .offset(offset)
    )
    
    results = await db.execute(query)
    
    polls = results.fetchall()
    
    for poll in polls:
        poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == poll[0].id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
        poll[0].body = poll_ques.ques_text
    
    return polls


async def get_post_poll(
    db: AsyncSession,
    post_id: UUID
):
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.id == post_id
        )
        .order_by(desc(Post.post_at))
    )
    
    results = await db.execute(query)
    post = results.fetchone()
    
    if not post:
        raise Exception("Post not found")
    if post[1].is_deleted:
        raise Exception("Post is deleted") 
    if post[1].is_blocked:
        raise Exception("Post is blocked")
    
    poll_items = await get_poll_post_items(db, post[0].id)
    
    return post, poll_items

async def get_member_poll_taken(
    db: AsyncSession,
    member_id: UUID,
    post_id: UUID
):
    
    query = (
        select(PollMemResult)
        .where(
            PollMemResult.member_id == member_id,
            PollMemResult.post_id == post_id
        )
    )
    results = await db.execute(query)
    
    poll_selected = results.fetchall()
    
    if not poll_selected:
        
        query = (
            select(PollMemReveal)
            .where(
                PollMemReveal.member_id == member_id,
                PollMemReveal.post_id == post_id
            )
        )
        results = await db.execute(query)
        poll_reveal = results.fetchone()
        if poll_reveal:
            return poll_reveal[0].reveal_at
        return None
    
    return poll_selected


#HOT OFF PRESS
async def get_hop_posts(
    db: AsyncSession,
    limit: int,
    offset: int,
    sort_type: str
) -> List:
    base_query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(
            Post.post_at >= (current_datetime() - timedelta(days=1)),
            PostStatusCurr.is_blocked == False,
            PostStatusCurr.is_deleted == False
        )
        .limit(limit)
        .offset(offset)
    )
    
    if sort_type == "newest":
        query = base_query.order_by(desc(Post.post_at))
    elif sort_type == "random":
        query = base_query.order_by(func.random())
    else:
        raise ValueError("Invalid sort_type. Must be 'newest' or 'random'.")

    results = await db.execute(query)
    posts = results.fetchall()
    return posts


#CLUB DAILY ANSWERS
async def get_cd_answers(
    db: AsyncSession,
    limit: int,
    offset: int
):
    query = (
        select(DailyAns, DailyQues.title, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(MemberProfileCurr, DailyAns.member_id == MemberProfileCurr.id)
        .join(DailyQues, DailyAns.ques_id == DailyQues.id)
        .where(
            DailyAns.is_deleted == False,
            DailyAns.is_blocked == False,
            func.date(DailyAns.post_at) == current_datetime().date(),
        )
        .order_by(desc(DailyAns.post_at))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    answers = results.fetchall()
    
    return answers


#MOST POPULAR
async def get_mp_posts(
    db: AsyncSession,
    limit: int,
    offset: int,
    interest: str
):
    
    where_clause_dict = {}

    if interest:
        where_clause_dict["Post.interest_id"] = interest
        where_clause_dict["PostStatusCurr.is_blocked"] = False
        where_clause_dict["PostStatusCurr.is_deleted"] = False
    else:
        where_clause_dict["PostStatusCurr.is_blocked"] = False
        where_clause_dict["PostStatusCurr.is_deleted"] = False

    query = (
        select(ViewPostScore, Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
        .join(Post, Post.id == ViewPostScore.post_id)
        .join(PostStatusCurr, PostStatusCurr.post_id == ViewPostScore.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
    )

    for table_column, value in where_clause_dict.items():
        table, column = table_column.split(".")
        mapped_table = globals()[table]
        query = query.where(getattr(mapped_table, column) == value)

    query = query.order_by(desc(ViewPostScore.post_score)).limit(PaginationLimit.random).offset(offset).limit(limit)

    result = await db.execute(query)
    post_scores = result.fetchall()

    return post_scores


#SEARCH POSTS
async def get_searched_posts(
    db: AsyncSession,
    search: str,
    limit: int,
    offset: int
):
    
    pgroonga_match_op = operators.custom_op('&@')

    raw_query = text("""
    SELECT 
    pst.post_posted.*, 
    post_status_curr.*, 
    mbr_profile_curr.df_img, 
    mbr_profile_curr.df_alias
    FROM 
        pst.post_posted
    JOIN 
        pst.post_status_curr 
        ON post_posted.post_id = post_status_curr.post_id
    JOIN 
        mbr.mbr_profile_curr 
        ON post_posted.mbr_id = mbr_profile_curr.mbr_id
    WHERE 
        (post_posted.tag1 &@ :search
        OR post_posted.tag2 &@ :search
        OR post_posted.tag3 &@ :search
        OR post_posted.post_title &@ :search
        OR post_posted.post_detail &@ :search)
        AND post_status_curr.is_blocked = FALSE
        AND post_status_curr.is_deleted = FALSE
    ORDER BY 
        post_posted.post_at DESC
    LIMIT :limit
    OFFSET :offset;
    """)

    query = (
            select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
            .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
            .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
            .where(
                or_(
                    Post.tag1.op('&@')(search),
                    Post.tag2.op('&@')(search),
                    Post.tag3.op('&@')(search),
                    Post.title.op('&@')(search),
                    Post.body.op('&@')(search),
                ),
                PostStatusCurr.is_blocked == False,
                PostStatusCurr.is_deleted == False
            )
            .order_by(desc(Post.post_at))
            .limit(limit)
            .offset(offset)
        )

    result = await db.execute(query)
    # result = await db.execute(raw_query, {"search": search, "limit": limit, "offset": offset})
    posts = result.fetchall()
    
    return posts


#GET RANDOM
async def get_random_sample_posts(session: AsyncSession, sample_size: int) -> List[Post]:
    
    stmt = text(f"SELECT * FROM pst.post_posted TABLESAMPLE SYSTEM({sample_size})")
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_random_posts_with_details(session: AsyncSession, sample_size: int) -> List:
    
    random_sample_posts = await get_random_sample_posts(session, sample_size)

    if not random_sample_posts:
        return []

    
    PostStatusCurrAlias = aliased(PostStatusCurr)
    MemberProfileCurrAlias = aliased(MemberProfileCurr)
    
    stmt = (
        select(Post, PostStatusCurrAlias, MemberProfileCurrAlias.image, MemberProfileCurrAlias.alias)
        .join(PostStatusCurrAlias, Post.id == PostStatusCurrAlias.post_id)
        .join(MemberProfileCurrAlias, Post.member_id == MemberProfileCurrAlias.id)
        .where(
            Post.id.in_(random_sample_posts),
            PostStatusCurrAlias.is_blocked == False,
            PostStatusCurrAlias.is_deleted == False
        )
    )

    result = await session.execute(stmt)
    return result.all()

async def get_random_posts(
    session: AsyncSession, 
    batch_size: int, 
    batch_count: int, 
    final_limit: int
) -> List:
    
    combined_posts = []
    
    for _ in range(batch_count):
        random_posts = await get_random_posts_with_details(session, batch_size)
        combined_posts.extend(random_posts)
    
    random.shuffle(combined_posts)
    
    return set(combined_posts[:final_limit])


#POSTS LIST CONVERTER
async def convert_blog_ques_post_for_response(post, member, tags):
    return PostBlogQuesResponse(
        post_id = str(post.id),
        member= member,

        title= post.title,
        body= post.body,
        type= post.type,

        interest_area_id= post.interest_id,
        language_id= post.lang_id,

        post_at= post.post_at,
        tags= tags,
    )

async def convert_normal_answer_post_for_response(db: AsyncSession, post, member):
    
    
    query = (
        select(Post.title)
        .where(Post.id == post.assc_post_id)
    )
    
    results = await db.execute(query)
    ques_title = results.scalar()
    
    return PostAnsResponse(
        post_id = str(post.id),
        member= member,

        type= post.type,

        title= ques_title,
        body= post.body,

        post_ques_id=str(post.assc_post_id),
        is_for_daily= False,

        post_at= post.post_at
    )
    
async def convert_poll_post_for_response(db:AsyncSession ,post, member, tags):
    
    poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == post.id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
    post.body = poll_ques.ques_text
    
    return PostBlogQuesResponse(
        post_id = str(post.id),
        member= member,
        
        type= post.type,
        title= post.title,
        body= post.body,
        
        tags= tags,
        interest_area_id= post.interest_id,
        language_id= post.lang_id,
        post_at= post.post_at
    )

async def convert_all_post_list_for_response(db, posts, n=0):
    res_posts = []
    
    for post_tuple in posts:
        
        if n == 0:
            post, post_status, image, alias = post_tuple
        elif n == 1:
            _ , post, post_status, image, alias = post_tuple
            
        member = get_member_dict_for_post_detail(post_status, image=image, alias= alias)

        if post.type == PostType.Question or post.type == PostType.Blog:

            tags = get_post_tags_list(post)

            res_posts.append(await convert_blog_ques_post_for_response(post, member, tags))
            
        elif post.type == PostType.Answer:

            res_posts.append(await convert_normal_answer_post_for_response(db, post, member))

        elif post.type == PostType.Poll:

            tags = get_post_tags_list(post)

            res_posts.append(await convert_poll_post_for_response(db, post, member, tags))  
            

    return res_posts


