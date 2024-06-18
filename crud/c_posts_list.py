import random
from sqlalchemy import exists, select, asc, delete, desc, func, and_, or_, text, Date, join
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from datetime import date

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from schemas.s_posts import InvitedQuesResponse, PostAnsResponse, PostBlogQuesResponse, PostPollResponse
from utilities.common import get_most_popular_base_func, get_random_posts_with_details, get_random_questions_polls_with_details, get_random_sample_posts, search_post_base_func
from utilities.constants import (
    INVALID_SORT_TYPE, PGROONGA_OPERATOR, POST_BLOCKED, POST_DELETED, POST_NOT_FOUND, AddType, ChoicesType, HOPSortType, PaginationLimit, PostType, current_datetime
)

from datetime import datetime, timedelta

from database.models import (
    DailyAns, DailyQues, MemberProfileCurr, PollInvite, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostStatusCurr, PostStatusHist, QuesInvite, ViewPostScore
)
from uuid_extensions import uuid7

from crud.c_posts import (
    get_poll_post_items,
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
    user_id: str = None
):
    member = {
            "image": user.image if user else image,
            "alias": user.alias if user else alias,
            "is_anonymous": post_curr.is_anonymous,
            "user_id": str(user.id) if user else str(user_id)
        }
    if post_curr.is_anonymous:
        member["alias"] = "Anonymous"
        member["image"] = None
        member["is_anonymous"] = post_curr.is_anonymous
        member["user_id"] = None
    
    return member




## DRAFTS ##

async def get_user_drafted_posts(
    db: AsyncSession,
    mem_id: UUID,
    post_type: str
):
    blogs = (await db.execute(select(PostDraft).where(PostDraft.member_id == mem_id, PostDraft.type == post_type).order_by(desc(PostDraft.save_at)))).scalars().all()
    
    if post_type == PostType.Poll:
        for poll in blogs:
            poll_ques = (await db.execute(select(PollQues).where(PollQues.post_id == poll.id, PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
            poll.body = poll_ques.ques_text

    return blogs

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

async def check_if_user_answered_question(
    db: AsyncSession,
    member_id: UUID,
    post_id: UUID
):
    query = (
        select(exists().where(
            Post.member_id == member_id,
            Post.type == PostType.Answer,
            Post.assc_post_id == post_id
        ))
    )
    results = await db.execute(query)
    exists_ = results.scalar()

    return exists_

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
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
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

    
#TAKE POLL AND QUESTION

async def get_random_post_questions_polls_list(
    db: AsyncSession,
    member_id: UUID,
    limit: int,
    sample_size: int,
    batch_count: int,
    post_type: str
):

    combined_posts = set()
    
    for _ in range(batch_count):
        random_posts = await get_random_questions_polls_with_details(db, sample_size, post_type, member_id)
        combined_posts.update(random_posts)
        
        if len(combined_posts) >= limit:
            break
    
    # random.shuffle(combined_posts)
    
    return set(combined_posts)

async def get_searched_question_poll_list(
    db: AsyncSession,
    member_id: UUID,
    search: str,
    limit: int,
    offset: int,
    post_type: str
):
    
    if post_type == PostType.Question:

        answered_subquery = (
            select(Post.assc_post_id)
            .where(
                Post.type == PostType.Answer,
                Post.member_id == member_id
            )
            .subquery()
        )

        filters = [
            Post.id.notin_(answered_subquery)
        ]
    elif post_type == PostType.Poll:
        
        poll_taken_subquery = (
            select(PollMemTake.post_id)
            .where(
                PollMemTake.member_id == member_id,               
            )
            .subquery()
        )
            
        poll_reveal_subquery = (
            select(PollMemReveal.post_id)
            .where(
                PollMemReveal.member_id == member_id,               
            )
            .subquery()
        )
        
        filters = [
            Post.id.notin_(poll_taken_subquery),
            Post.id.notin_(poll_reveal_subquery)
        ]
        
    else:
        raise Exception("Invalid Post Type")
    
    
    where_clause = {
        "Post.type": post_type,
    }
    
    
    query = await search_post_base_func(where_clause, filters)

    query = query.order_by(desc(Post.post_at)).limit(limit).offset(offset)
    

    result = await db.execute(query, {'search': search})
    posts = result.fetchall()
    
    return posts


async def invited_question_poll_response(
    db: AsyncSession,
    invited: List[Tuple[UUID, int, bool]],
    type: str
):
    
    res = []
    
    if type == PostType.Question:
        
        for invite in invited:
            
            post_query = (
                select(
                    Post.title,
                    Post.body,
                    Post.post_at,
                    MemberProfileCurr.alias,
                    MemberProfileCurr.image,
                    MemberProfileCurr.id
                )
                .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
                .where(Post.id == invite[0])
            )
            
            results = await db.execute(post_query)
            post = results.fetchone()
            
            image_query = (
                select(MemberProfileCurr.image)
                .join(MemberProfileCurr, MemberProfileCurr.id == QuesInvite.inviting_mbr_id)
                .where(QuesInvite.ques_post_id == invite[0])
                .limit(PaginationLimit.invited_images)
            )

            results = await db.execute(image_query)
            images = results.fetchall()


            inv_dict = {
                "count": invite[1],
                "images": [img[0] for img in images]
            }

            _curr = PostStatusCurr(
                is_anonymous=invite[2]
            )

            member = get_member_dict_for_post_detail(_curr, image=post[-2], alias=post[-3], user_id=post[-1])
            
            res.append(InvitedQuesResponse(
                post_id=str(invite[0]),
                member=member,

                type= PostType.Question,

                title= post[0],
                body= post[1],
                post_at= post[2],
                
                invited=inv_dict
            ))
        
    elif type == PostType.Poll:

        for invite in invited:

            post_query = (
                select(
                    Post.title,
                    Post.post_at,
                    MemberProfileCurr.alias,
                    MemberProfileCurr.image,
                    MemberProfileCurr.id
                )
                .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
                .where(Post.id == invite[0])
            )

            results = await db.execute(post_query)
            post = results.fetchone()

            body = (await db.execute(select(PollQues.ques_text).where(PollQues.post_id == invite[0], PollQues.qstn_seq_num == 1, PollQues.ans_seq_letter == "A"))).scalar()
            
            image_query = (
                select(MemberProfileCurr.image)
                .join(MemberProfileCurr, MemberProfileCurr.id == QuesInvite.inviting_mbr_id)
                .where(QuesInvite.ques_post_id == invite[0])
                .limit(PaginationLimit.invited_images)
            )

            results = await db.execute(image_query)
            images = results.fetchall()

            inv_dict = {
                "count": invite[1],
                "images": [img[0] for img in images]
            }

            _curr = PostStatusCurr(
                is_anonymous=invite[2]
            )

            member = get_member_dict_for_post_detail(_curr, image=post[-2], alias=post[-3], user_id=post[-1])
            
            res.append(InvitedQuesResponse(
                post_id=str(invite[0]),
                member=member,

                type= PostType.Question,

                title= post[0],
                body= body,
                post_at= post[1],
                
                invited=inv_dict
            ))

    return res
    

async def get_invited_question_poll_list(
    db: AsyncSession,
    member_id: UUID,
    limit: int,
    offset: int,
    post_type: str
):
    
    if post_type == PostType.Question:
        query = (
            select(
                QuesInvite.ques_post_id,
                func.count(func.distinct(QuesInvite.inviting_mbr_id)).label('invites_count'),
                PostStatusCurr.is_anonymous
            )
            .join(PostStatusCurr, QuesInvite.ques_post_id == PostStatusCurr.post_id)
            .where(
                QuesInvite.invited_mbr_id == member_id,
                PostStatusCurr.is_deleted == False,
                PostStatusCurr.is_blocked == False
            )
            .group_by(QuesInvite.ques_post_id)
        )
        
    elif post_type == PostType.Poll:
        query = (
            select(
                PollInvite.poll_post_id,
                func.count(func.distinct(PollInvite.inviting_mbr_id)).label('invites_count')       ,
                PostStatusCurr.is_anonymous
            )
            .join(PostStatusCurr, PollInvite.poll_post_id == PostStatusCurr.post_id)
            .where(
                PollInvite.invited_mbr_id == member_id,
                PostStatusCurr.is_deleted == False,
                PostStatusCurr.is_blocked == False
            )
            .group_by(PollInvite.poll_post_id)
        )
        
    else:
        raise Exception("Invalid Post Type")
    
    query = query.limit(limit).offset(offset)
    
    results = await db.execute(query)
    posts = results.fetchall()
    
    if posts:
        invited = await invited_question_poll_response(posts, post_type)
    else:
        invited = []
        
    return invited





async def get_post_question(
    db: AsyncSession,
    post_id: UUID,
    limit: int ,
    offset: int
) -> Tuple[Tuple[Post, PostStatusCurr, str, str, str], List[Tuple[Post, PostStatusCurr, str, str, str]]]:
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
        .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
        .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
        .where(Post.id == post_id)
    )
    results = await db.execute(query)
    post = results.fetchone()
    
    if not post:
        raise Exception(POST_NOT_FOUND)
    if post[1].is_deleted:
        raise Exception(POST_DELETED) 
    if post[1].is_blocked:
        raise Exception(POST_BLOCKED)
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
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
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
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
    post_id: UUID,
    get_percentage: bool = False
):
    
    query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
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
        raise Exception(POST_NOT_FOUND)
    if post[1].is_deleted:
        raise Exception(POST_DELETED) 
    if post[1].is_blocked:
        raise Exception(POST_BLOCKED)
    
    poll_items = await get_poll_post_items(db, post[0].id, get_percentage)
    
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
    
    return poll_selected


#HOT OFF PRESS
async def get_hop_posts(
    db: AsyncSession,
    limit: int,
    offset: int,
    sort_type: str
) -> List:
    base_query = (
        select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
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
    
    if sort_type == HOPSortType.newest:
        query = base_query.order_by(desc(Post.post_at))
    elif sort_type == HOPSortType.random:
        query = base_query.order_by(func.random())
    else:
        raise ValueError(INVALID_SORT_TYPE)

    results = await db.execute(query)
    posts = results.fetchall()
    return posts


#CLUB DAILY ANSWERS
async def get_cd_ques_list(
    db: AsyncSession,
    query_date: date,
    limit: int,
    offset: int
):
    
    latest_answer_subquery = (
        select(
            DailyAns.ques_id,
            func.max(DailyAns.post_at).label('latest_post_at')
        )
        .where(
            func.cast(DailyAns.post_at, Date) == query_date,
            DailyAns.is_deleted == False,
            DailyAns.is_blocked == False
        )
        .group_by(DailyAns.ques_id)
        .subquery()
    )

    query = (
        select(
            DailyQues.id,
            DailyQues.title,
            DailyAns.id,
            DailyAns.answer,
            DailyAns.post_at,
            MemberProfileCurr.alias,
            MemberProfileCurr.image,
            DailyAns.member_id,
            DailyAns.is_anonymous
        )
        .outerjoin(latest_answer_subquery, DailyQues.id == latest_answer_subquery.c.ques_id)
        .outerjoin(DailyAns, and_(
            DailyQues.id == DailyAns.ques_id,
            DailyAns.post_at == latest_answer_subquery.c.latest_post_at
        ))
        .outerjoin(MemberProfileCurr, MemberProfileCurr.id == DailyAns.member_id)
        .where(DailyQues.is_live == True)
        .order_by(desc(DailyAns.post_at))
        .limit(limit)
        .offset(offset)
    )

    results = await db.execute(query)
    answers = results.fetchall()
    
    return answers

async def club_daily_post_answers(
    db: AsyncSession,
    post_id: UUID,
    query_date: date,
    limit: int,
    offset: int
):

    query = (
        select(DailyAns, MemberProfileCurr.alias, MemberProfileCurr.image)
        .join(MemberProfileCurr, DailyAns.member_id == MemberProfileCurr.id)
        .where(
            DailyAns.ques_id == post_id,
            DailyAns.is_deleted == False,
            DailyAns.is_blocked == False,
            func.cast(DailyAns.post_at, Date) == query_date
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
    
    where_clause_dict = {
        "PostStatusCurr.is_blocked": False,
        "PostStatusCurr.is_deleted": False
    }

    if interest:
        where_clause_dict["Post.interest_id"] = interest


    query = await get_most_popular_base_func(where_clause_dict)

    query = query.order_by(desc(ViewPostScore.post_score)).limit(PaginationLimit.most_popular).offset(offset).limit(limit)

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

    query = await search_post_base_func()
    
    query = query.order_by(desc(Post.post_at)).limit(limit).offset(offset)
    
    # query = (
    #         select(Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias, MemberProfileCurr.id)
    #         .join(PostStatusCurr, Post.id == PostStatusCurr.post_id)
    #         .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
    #         .where(
    #             or_(
    #                 text(f"pst.post_posted.tag1_std {PGROONGA_OPERATOR} :search"),
    #                 text(f"pst.post_posted.tag2_std {PGROONGA_OPERATOR} :search"),
    #                 text(f"pst.post_posted.tag3_std {PGROONGA_OPERATOR} :search"),
    #                 text(f"pst.post_posted.post_title {PGROONGA_OPERATOR} :search"),
    #                 text(f"pst.post_posted.post_detail {PGROONGA_OPERATOR} :search"),
    #             ),
    #             PostStatusCurr.is_blocked == False,
    #             PostStatusCurr.is_deleted == False
    #         )
    #         .order_by(desc(Post.post_at))
    #         .limit(limit)
    #         .offset(offset)
    #     )

    result = await db.execute(query, {'search': search})
    posts = result.fetchall()
    
    return posts


#GET RANDOM
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
            post, post_status, image, alias, user_id = post_tuple
        elif n == 1:
            _ , post, post_status, image, alias, user_id = post_tuple
            
        member = get_member_dict_for_post_detail(post_status, image=image, alias= alias, user_id= user_id)

        if post.type == PostType.Question or post.type == PostType.Blog:

            tags = get_post_tags_list(post)

            res_posts.append(await convert_blog_ques_post_for_response(post, member, tags))
            
        elif post.type == PostType.Answer:

            res_posts.append(await convert_normal_answer_post_for_response(db, post, member))

        elif post.type == PostType.Poll:

            tags = get_post_tags_list(post)

            res_posts.append(await convert_poll_post_for_response(db, post, member, tags))  
            

    return res_posts


