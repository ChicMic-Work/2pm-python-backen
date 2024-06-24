from sqlalchemy import exists, func, or_, select, asc, delete, desc, and_
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from uuid_extensions import uuid7

from typing import List, Tuple

from crud.c_profile import get_follow_counts_search
from schemas.s_posts_actions import MemInvSentList, MemInviteListBase, ReportReasonReq
from utilities.constants import (
    INVALID_POLL_ITEM, INVALID_POST_TYPE, POLL_ALREADY_REVEALED, POLL_ALREADY_TAKEN, POST_BLOCKED, POST_DELETED, REPORT_ALREADY_EXISTS, AddType, ChoicesType, PostInviteListType, PostType, ReportType
)

from database.models import (
    DailyAns, MemberProfileCurr, MmbFollowCurr, MmbMsgReport, MmbReport, PollInvite, PollMemResult, PollMemReveal, PollMemTake, PollQues, Post,
    PostDraft, PostFavCurr, PostFavHist, PostFolCurr, PostFolHist, PostLikeCurr, PostLikeHist, PostStatusCurr, PostStatusHist, QuesInvite, ViewMmbTag
)
from uuid_extensions import uuid7

#CHECK POST CURRENT STATUS
async def check_post_curr_details(
    db: AsyncSession,
    post_id: UUID
):
    
    query = (
        select(PostStatusCurr)
        .where(
            PostStatusCurr.post_id == post_id
        )
    )
    
    results = await db.execute(query)
    post_curr = results.fetchone()
    
    if post_curr[0].is_deleted:
        raise Exception(POST_DELETED) 
    if post_curr[0].is_blocked:
        raise Exception(POST_BLOCKED)
    
    return post_curr

#TAKE POLL
async def check_if_poll_items_exist(
    db: AsyncSession,
    post_id: UUID,
    poll_item_ids: List[UUID]
):
    query = (
        select(PollQues)
        .where(
            and_(
                PollQues.post_id == post_id,
                PollQues.poll_item_id.in_(poll_item_ids)
            )
        )
    )
    
    results = await db.execute(query)
    poll_items = results.scalars().all()
    
    if len(poll_items) != len(poll_item_ids):
        raise Exception(INVALID_POLL_ITEM)

    return poll_items

async def check_if_user_took_poll(
    db: AsyncSession,
    user_id: UUID,
    post_id: UUID,
    raise_exc: bool = True
):
    query = (
        select(PollMemTake)
        .where(
            PollMemTake.member_id == user_id,
            PollMemTake.post_id == post_id
        )
    )

    results = await db.execute(query)
    mem_take = results.fetchone()

    if mem_take and raise_exc:
        raise Exception(POLL_ALREADY_TAKEN)
    
    if mem_take and not raise_exc:
        return mem_take, "take"
    
    query = (
        select(PollMemReveal)
        .where(
            PollMemReveal.post_id == post_id,
            PollMemReveal.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_reveal = results.fetchone()

    if mem_reveal and raise_exc:
        raise Exception(POLL_ALREADY_REVEALED)
    
    if mem_reveal and not raise_exc:
        return mem_reveal, "reveal"
    

async def member_create_poll_entries(
    db: AsyncSession,
    post_id: UUID,
    user_id: UUID,
    poll_items: List[PollQues]
):
    # Check if the selected items are valid according to the allow_multiple flag
    questions = {}
    for item in poll_items:
        if item.qstn_seq_num not in questions:
            questions[item.qstn_seq_num] = []
        questions[item.qstn_seq_num].append(item)
    
    for seq_num, items in questions.items():
        allow_multiple = items[0].allow_multiple
        if not allow_multiple and len(items) > 1:
            raise Exception(f"Multiple choices are not allowed for question {seq_num}")

    new_entries = [
        PollMemResult(
            poll_item_id=poll_item.poll_item_id,
            post_id=post_id,
            member_id=user_id
        )
        for poll_item in poll_items
    ]
    
    poll_take = PollMemTake(
        post_id=post_id,
        member_id=user_id
    )
    
    return new_entries, poll_take
    
    
async def check_member_reveal_took_poll(
    db: AsyncSession,
    post_id: UUID,
    user_id: UUID
):
    
    query = (
        select(PollMemReveal)
        .where(
            PollMemReveal.post_id == post_id,
            PollMemReveal.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_reveal = results.fetchone()

    if mem_reveal:
        raise Exception(POLL_ALREADY_REVEALED)
    
    query = (
        select(PollMemTake)
        .where(
            PollMemTake.post_id == post_id,
            PollMemTake.member_id == user_id
        )
    )

    results = await db.execute(query)
    mem_take = results.fetchone()
    if mem_take:
        raise Exception(POLL_ALREADY_TAKEN)
    
    reveal = PollMemReveal(
        post_id=post_id,
        member_id=user_id
    )
    
    return reveal



#INVITE
async def invite_member_to_post(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    inviting_user_id: UUID
):
    if post.type == PostType.Question:
        
        _invited = QuesInvite(
            ques_post_id=post.id,
            inviting_mbr_id=inviting_user_id,
            invited_mbr_id= user_id
        )
        
    elif post.type == PostType.Poll:
        
        _invited = PollInvite(
            poll_post_id=post.id,
            inviting_mbr_id=inviting_user_id,
            invited_mbr_id= user_id
        )
        
    else:
        raise Exception(INVALID_POST_TYPE)
    
    return _invited



async def invite_member_to_post_list(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    limit: int,
    offset: int,
    type: str = PostInviteListType.FOLLOWERS,
    search: str = ""
):

    if post.type == PostType.Question:
            
        invited_subquery = (
            select(QuesInvite.invited_mbr_id)
            .where(QuesInvite.ques_post_id == post.id)
            .subquery()
        )
        
        answered_subquery = (
            select(Post.member_id)
            .where(Post.assc_post_id == post.id)
            .subquery()
        )
        
        filters = [
            MemberProfileCurr.id.notin_(answered_subquery)
        ]
            
    else: 
        
        invited_subquery = (
            select(PollInvite.invited_mbr_id)
            .where(PollInvite.poll_post_id == post.id)
            .subquery()
        )
        
        poll_taken_subquery = (
            select(PollMemTake.member_id)
            .where(
                PollMemTake.post_id == post.id,               
            )
            .subquery()
        )
        
        poll_reveal_subquery = (
            select(PollMemReveal.member_id)
            .where(
                PollMemReveal.post_id == post.id,               
            )
            .subquery()
        )
        
        filters = [
            MemberProfileCurr.id.notin_(poll_taken_subquery),
            MemberProfileCurr.id.notin_(poll_reveal_subquery)
        ]

    base_query = (
        select(
            MemberProfileCurr.alias,
            MemberProfileCurr.id,
            MemberProfileCurr.image,
            MemberProfileCurr.bio,
            # MmbFollowCurr.follow_at,
            exists(invited_subquery.c.invited_mbr_id)
                .where(invited_subquery.c.invited_mbr_id == MemberProfileCurr.id)
                .label("invited_already"),
        )
    )
    
    
    
    if type == PostInviteListType.FOLLOWERS:
        query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.following_id).where(
            MmbFollowCurr.followed_id == user_id
        )
        
        check_following = True
            
    elif type == PostInviteListType.FOLLOWING:
        query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.followed_id).where(
            MmbFollowCurr.following_id == user_id
        )
        
        check_following = False
    
    else:
        raise Exception("INVALID_INVITE_LIST_TYPE")
    
    if search:
        search_filter = MemberProfileCurr.alias.ilike(f"%{search}%")
        query = query.where(search_filter)
    
    for filter in filters:
        query = query.where(filter)
    
    query = query.limit(limit).offset(offset)
    """
    if search:
        
        combined_query = base_query.join(
            MmbFollowCurr, 
                or_(
                    MemberProfileCurr.id == MmbFollowCurr.following_id,
                    MemberProfileCurr.id == MmbFollowCurr.followed_id
                )
            ).where(
                or_(
                    MmbFollowCurr.following_id == user_id,
                    MmbFollowCurr.followed_id == user_id
                )
            )
        
        search_filter = MemberProfileCurr.alias.ilike(f"%{search}%")
        combined_query = combined_query.where(search_filter)

        for filter in filters:
            combined_query = combined_query.where(filter)

        query = combined_query.distinct(MemberProfileCurr.id).limit(limit).offset(offset) #.order_by(MemberProfileCurr.id, MmbFollowCurr.follow_at.desc())
        
        check_following = True
        
    else:
        if type == PostInviteListType.FOLLOWERS:
            query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.following_id).where(
                MmbFollowCurr.followed_id == user_id
            )
            
            check_following = True
                
        elif type == PostInviteListType.FOLLOWING:
            query = base_query.join(MmbFollowCurr, MemberProfileCurr.id == MmbFollowCurr.followed_id).where(
                MmbFollowCurr.following_id == user_id
            )
            
            check_following = False
        
        else:
            raise Exception("INVALID_INVITE_LIST_TYPE")

        for filter in filters:
            query = query.where(filter)

        query = query.limit(limit).offset(offset) #.order_by(desc(MmbFollowCurr.follow_at))
    """
    
    res = await db.execute(query)
    users = res.fetchall()
    
    users_data = []
    
    for user in users:
        
        follow_counts = await get_follow_counts_search(db, user[1], user_id, check_following)
        
        users_data.append({
            "id": user[1],
            "alias": user[0],
            "image": user[2],
            "bio": user[3],
            "invited_already": user[-1],
            "followers_count": follow_counts["followers_count"],
            "following_count": follow_counts["following_count"],
            "is_following": follow_counts["is_following"],
        })
    
    return users_data



async def recommend_member_to_post_list(
    db: AsyncSession,
    post: Post,
    user_id: int,
    limit: int = 10,
    offset: int = 0
):
    
    if post.type == PostType.Question:
            
        invited_subquery = (
            select(QuesInvite.invited_mbr_id)
            .where(QuesInvite.ques_post_id == post.id,
                   QuesInvite.inviting_mbr_id == user_id)
            .subquery()
        )
    elif post.type == PostType.Poll:
        
        invited_subquery = (
            select(PollInvite.invited_mbr_id)
            .where(PollInvite.poll_post_id == post.id,
                   PollInvite.inviting_mbr_id == user_id)
            .subquery()
        )
    
    PostAlias = aliased(Post)
    ViewMmbTagAlias = aliased(ViewMmbTag)
    
    post_tags_subquery = (
        select(
            PostAlias.tag1_std,
            PostAlias.tag2_std,
            PostAlias.tag3_std,
            PostAlias.member_id.label('post_creator')
        )
        .where(PostAlias.id == post.id)
        .subquery()
    )
    
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
    
    recommended_users_query = (
        select(
            MemberProfileCurr.alias,
            tag_usage_subquery.c.member_id,
            MemberProfileCurr.image,
            MemberProfileCurr.bio,
            exists(invited_subquery.c.invited_mbr_id)
                .where(invited_subquery.c.invited_mbr_id == MemberProfileCurr.id)
                .label("invited_already")
        )
        .join(MemberProfileCurr, tag_usage_subquery.c.member_id == MemberProfileCurr.id)
        .order_by(tag_usage_subquery.c.matching_tags.desc(), tag_usage_subquery.c.total_count.desc())
        .limit(limit)
        .offset(offset)
    )

    res = await db.execute(recommended_users_query)
    users = res.fetchall()
    
    users_data = []
    
    if users:
        for user in users:
            
            follow_counts = await get_follow_counts_search(db, user[1], user_id, False)
            
            users_data.append({
                "id": user[1],
                "alias": user[0],
                "image": user[2],
                "bio": user[3],
                "invited_already": user[-1],
                "followers_count": follow_counts["followers_count"],
                "following_count": follow_counts["following_count"],
                "is_following": follow_counts["is_following"]
            })
    else:
        pass
        #fuzzy records
    
    return users_data



async def invite_mem_post_response(
    db: AsyncSession,
    invites,
    post: Post,
    invite_type: str   
):
    
    res_data = []
    
    if invite_type == PostInviteListType.RECEIVED:
        
        for invite in invites:
            
            query = (
                select(
                    MemberProfileCurr.alias,
                    MemberProfileCurr.image
                )
                .where(MemberProfileCurr.id == invite[0])
            )
            result = await db.execute(query)
            user = result.fetchone()
            
            follow_dict = await get_follow_counts_search(db, invite[0], None, False)
            
            res_data.append(MemInviteListBase(
                id = invite[0],
                alias = user[0],
                image = user[1],
                followers_count= follow_dict["followers_count"],
                following_count= follow_dict["following_count"],
                invite_at = invite[1]
            ))
            
    elif invite_type == PostInviteListType.SENT:
        
        for invite in invites:
            
            query = (
                    select(
                        MemberProfileCurr.alias,
                        MemberProfileCurr.image
                    )
                    .where(MemberProfileCurr.id == invite[0])
                )
            result = await db.execute(query)
            user = result.fetchone()   
            
            follow_dict = await get_follow_counts_search(db, invite[0], None, False)
            
            res_data.append(MemInvSentList(
                id = invite[0],
                alias = user[0],
                image = user[1],
                invite_at = invite[1],
                answer_id = invite[2] if post.type== PostType.Question else None,
                followers_count= follow_dict["followers_count"],
                following_count= follow_dict["following_count"]
            ))
    
    return res_data
    



async def invite_mem_post_list(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    limit: int,
    offset: int,
    type: str = PostInviteListType.RECEIVED,
):
    
    if type == PostInviteListType.RECEIVED:
        
        if post.type == PostType.Question:
        
            query = (
                select(
                    QuesInvite.inviting_mbr_id,
                    QuesInvite.invite_at
                )
                .where(
                    QuesInvite.ques_post_id == post.id,
                    QuesInvite.invited_mbr_id == user_id
                )
            )
        
        elif post.type == PostType.Poll:
        
            query = (
                select(
                    PollInvite.inviting_mbr_id,
                    PollInvite.invite_at
                )
                .where(
                    PollInvite.poll_post_id == post.id,
                    PollInvite.invited_mbr_id == user_id
                )
            )
        
    elif type == PostInviteListType.SENT:
        
        if post.type == PostType.Question:
        
            query = (
                select(
                    QuesInvite.invited_mbr_id,
                    QuesInvite.invite_at,
                    QuesInvite.ans_post_id
                )
                .where(
                    QuesInvite.ques_post_id == post.id,
                    QuesInvite.inviting_mbr_id == user_id
                )
            )
        
        elif post.type == PostType.Poll:
        
            query = (
                select(
                    PollInvite.invited_mbr_id,
                    PollInvite.invite_at,
                )
                .where(
                    PollInvite.poll_post_id == post.id,
                    PollInvite.inviting_mbr_id == user_id
                )
            )
            
    else:
        raise Exception("INVALID_INVITE_LIST_TYPE")
    
    res = await db.execute(query)
    invites = res.fetchall()
    res_data = []
    
    if invites:
        res_data = await invite_mem_post_response(db, invites, post, type)
        
    
    return res_data






#FOLLOW POSTS 
async def member_follow_ques_poll(
    db: AsyncSession,
    member_id: UUID,
    post: Post
):
    
    _del = None
    
    _hist = PostFolHist(
        post_id = post.id,
        member_id = member_id,
        add_type = AddType.Add
    )
    
    query = (
        select(PostFolCurr)
        .where(
            PostFolCurr.post_id == post.id,
            PostFolCurr.member_id == member_id
        )
    )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        _del = result
        _hist.add_type = AddType.Delete 
        
    else:
        result = PostFolCurr(
            member_id = member_id,
            post_id = post.id
        )
    
    return _del, _hist, result


#FAVORITE POSTS
async def member_mark_fav_post(
    db: AsyncSession,
    member_id: UUID,
    post: Post
):
    _del = None
    
    _hist = PostFavHist(
        post_id = post.id,
        member_id = member_id,
        add_type = AddType.Add
    )
    
    query = (
        select(PostFavCurr)
        .where(
            PostFavCurr.post_id == post.id,
            PostFavCurr.member_id == member_id
        )
    )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        _del = result
        _hist.add_type = AddType.Delete 
        
    else:
        result = PostFavCurr(
            member_id = member_id,
            post_id = post.id
        )
    
    return _del, _hist, result


async def member_like_post(
    db: AsyncSession,
    member_id: UUID,
    post: Post
):
    _del = None
    
    _hist = PostLikeHist(
        post_id = post.id,
        member_id = member_id,
        add_type = AddType.Add
    )
    
    query = (
        select(PostLikeCurr)
        .where(
            PostLikeCurr.post_id == post.id,
            PostLikeCurr.member_id == member_id
        )
    )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        _del = result
        _hist.add_type = AddType.Delete 
        
    else:
        result = PostLikeCurr(
            member_id = member_id,
            post_id = post.id
        )
    
    return _del, _hist, result



async def check_existing_report(
    db: AsyncSession,
    member_id: UUID,
    content_id: UUID,
    message: bool
):
    if message:
        
        query = (
            select(exists().where(
                MmbMsgReport.conversation_id == content_id,
                MmbMsgReport.reporting_member == member_id
            ))
        )
        
    else:
        query = (
            select(exists().where(
                MmbReport.report_content_id == content_id,
                MmbReport.reporting_id == member_id
            ))
        )
    
    result = (await db.execute(query)).scalar()
    
    if result:
        raise Exception(REPORT_ALREADY_EXISTS)



async def member_report_content(
    db: AsyncSession,
    member_id: UUID,
    content_id: UUID,
    reason: ReportReasonReq,
):
    if reason.content_type != ReportType.MESSAGE:
        return MmbReport(
            reporting_id = member_id,
            report_content_type = reason.content_type,
            report_content_id = content_id,
            content = reason.content,
            reason_code = reason.reason,
            reason_other_text = reason.reason_text,
        )
        
    return MmbMsgReport(
        
    )