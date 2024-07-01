from fastapi import (
    APIRouter, Depends, 
    HTTPException, Header, 
    Request, UploadFile,
    File, Response
)
from sqlalchemy import delete, exists, select
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession

from crud.c_posts import (
    add_ans_to_invited_ques, create_a_post_comment, create_ans_post_crud, create_blog_post_crud, create_draft_ans_post_crud, 
    create_draft_blog_post_crud, create_draft_poll_post_crud, create_forum_tag, create_poll_post_crud,
    create_ques_post_crud, create_draft_ques_post_crud, get_poll_post_items, update_ans_posts_to_deleted, update_post_comments_to_deleted, update_post_hist_to_deleted
)
from crud.c_posts_actions import check_post_curr_details
from crud.c_posts_list import get_member_dict_for_post_detail, get_post_tags_list
from dependencies import get_db

from crud.c_auth import (
    get_user_by_id
)

from utilities.constants import (
    CANT_DELETE_COMMENT, CANT_DELETE_DRAFT, CANT_DELETE_POST, COMMENT_NOT_FOUND, DAILY_QUES_NOT_FOUND, DRAFT_CREATED, DRAFT_NOT_FOUND, POST_CREATED, POST_NOT_FOUND, 
    QUES_NOT_FOUND, AuthTokenHeaderKey, PostType, ResponseKeys, ResponseMsg, current_datetime
)

from schemas.s_posts import (
    PostAnsDraftRequest,
    PostAnsRequest,
    PostAnsResponse,
    PostBlogDraftRequest,
    PostBlogQuesResponse,
    # PostCreateRequest,
    PostBlogRequest,
    PostCommentRequest,
    PostPollDraftRequest,
    PostPollRequest,
    PostPollResponse,
    PostQuesDraftRequest,
    PostQuesRequest
)

from database.models import (
    CommentNode, DailyAns, DailyCommentNode, DailyQues, MemberProfileCurr, PollQues, Post,
    PostDraft, PostStatusCurr
)


router = APIRouter(
    prefix='/posts',
    tags=['posts'],
)


#BLOG
@router.post(
    "/create/blog/"
    )
async def create_blog_post(
    request: Request,
    post_request: PostBlogRequest,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user
            
            del_query, post, post_curr, post_hist = await create_blog_post_crud(db, user.id, post_request.draft_id, post_request)
            
            add_tag = []
            for tag in post_request.tags:
                _tag = await create_forum_tag(db, tag)
                if _tag:
                    add_tag.append(_tag)
            
            db.add_all(add_tag)

            db.add(post)
            db.add(post_curr)
            db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
            
            msg = POST_CREATED
            
            tags = get_post_tags_list(post)
            
            member = get_member_dict_for_post_detail(post_curr, user)

            res_data = PostBlogQuesResponse(
                post_id = str(post.id),
                member= member,
                
                title= post.title,
                body= post.body,
                type= post.type,
                
                interest_area_id= post.interest_id,
                language_id= post.lang_id,
                
                post_at= post.post_at,
                tags= tags
            )
            
            return {
                ResponseKeys.MESSAGE : msg,
                ResponseKeys.DATA: res_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/blog/"
    )
async def create_draft_blog_post(
    request: Request,
    response: Response,
    draft_request: PostBlogDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user
        
        draft = await create_draft_blog_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#QUESTION
@router.post(
    "/create/question/"
)
async def create_question_post(
    request: Request,
    response: Response,
    post_request: PostQuesRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user

            del_query, post, post_curr, post_hist = await create_ques_post_crud(db, user.id, post_request.draft_id, post_request)
            
            add_tag = []
            for tag in post_request.tags:
                _tag = await create_forum_tag(db, tag)
                if _tag:
                    add_tag.append(_tag)
            
            db.add_all(add_tag)

            db.add(post)
            db.add(post_curr)
            db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
                
            tags = get_post_tags_list(post)
            
            member = get_member_dict_for_post_detail(post_curr, user)

            res_data = PostBlogQuesResponse(
                post_id = str(post.id),
                member= member,
                
                title= post.title,
                body= post.body,
                type= post.type,
                
                interest_area_id= post.interest_id,
                language_id= post.lang_id,
                
                post_at= post.post_at,
                tags= tags
            )
            
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: res_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/question/"
    )
async def create_draft_question_post(
    request: Request,
    response: Response,
    draft_request: PostQuesDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        draft = await create_draft_ques_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#ANSWER
@router.post(
    "/create/answer/"
    )
async def create_answer_post(
    request: Request,
    response: Response,
    post_request: PostAnsRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            
            user: MemberProfileCurr = request.user

            ques  = await db.get(DailyQues, post_request.post_ques_id)
            if not ques and post_request.is_for_daily:
                raise Exception(DAILY_QUES_NOT_FOUND)
            if ques and not post_request.is_for_daily:
                post_request.is_for_daily = True
                
            if not post_request.is_for_daily:
                ques = await db.get(Post, post_request.post_ques_id)
                if not ques:
                    raise Exception(QUES_NOT_FOUND)
            
            del_query, post, post_curr, post_hist  = await create_ans_post_crud(db, user.id, post_request.draft_id, post_request, ques)

            invites = None
            invite_true = False
            if post_curr and not post_curr.is_anonymous:
                invite_true = True
                invites = await add_ans_to_invited_ques(db, ques, post, user.id)
            
            db.add(post)
            
            if post_curr:
                db.add(post_curr)
            if post_hist:
                db.add(post_hist)

            if post_request.draft_id:
                await db.execute(del_query)
            if invite_true:
                await db.execute(invites)
            
            post_type = PostType.Answer
            
            if post_curr:
                _curr = post_curr
            else:
                _curr = PostStatusCurr(
                    is_anonymous= post_request.is_anonymous,
                )
            
            member = get_member_dict_for_post_detail(_curr, user)
            
            req_data = PostAnsResponse(
                post_id = str(post.id),
                member= member,
                
                type= post_type,
                
                title= post_request.title,
                body= post_request.body,
                
                post_ques_id=str(post_request.post_ques_id),
                is_for_daily= post_request.is_for_daily,
                
                post_at= post.post_at
            )
            
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: req_data
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/answer/"
    )
async def create_draft_answer_post(
    request: Request,
    response: Response,
    draft_request: PostAnsDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        ques  = await db.get(DailyQues, draft_request.post_ques_id)
        if not ques and draft_request.is_for_daily:
            raise Exception(DAILY_QUES_NOT_FOUND)
        if ques and not draft_request.is_for_daily:
            draft_request.is_for_daily = True

        if not draft_request.is_for_daily:
            ques = await db.get(Post, draft_request.post_ques_id)
            if not ques:
                raise Exception(QUES_NOT_FOUND)
        
        draft = await create_draft_ans_post_crud(db, user.id, draft_request.draft_id, draft_request, ques)

        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }



#POLL
@router.post(
    "/create/poll/"
    )
async def create_poll_post(
    request: Request,
    response: Response,
    post_request: PostPollRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    
        try:
            async with db.begin_nested():
                user: MemberProfileCurr = request.user
                
                
                
                del_queries, post, post_curr, post_hist, ques_list = await create_poll_post_crud(db, user.id, post_request.draft_id, post_request)
                
                add_tag = []
                for tag in post_request.tags:
                    _tag = await create_forum_tag(db, tag)
                    if _tag:
                        add_tag.append(_tag)
                
                db.add_all(add_tag)
                
                db.add(post)
                db.add(post_curr)
                db.add(post_hist)
                db.add_all(ques_list)

                if post_request.draft_id:
                    for del_query in del_queries:
                        await db.execute(del_query)
                
                tags = get_post_tags_list(post)
                    
                member = get_member_dict_for_post_detail(post_curr, user)
                
            async with db.begin_nested():
                
                poll = await get_poll_post_items(db, post.id)
                
                req_data = PostPollResponse(
                    post_id = str(post.id),
                    member= member,
                    
                    type= post.type,
                    title= post.title,
                    body= post.body,
                    
                    tags= tags,
                    interest_area_id= post.interest_id,
                    language_id= post.lang_id,
                    
                    post_at= post.post_at,
                    poll= poll
                )

                await db.commit()
                
            return {
                ResponseKeys.MESSAGE: POST_CREATED,
                ResponseKeys.DATA: req_data
            }

        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }


@router.post(
    "/draft/poll/"
    )
async def create_draft_poll_post(
    request: Request,
    response: Response,
    draft_request: PostPollDraftRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    try:
        user: MemberProfileCurr = request.user

        del_query, draft, ques_list = await create_draft_poll_post_crud(db, user.id, draft_request.draft_id, draft_request)

        db.add(draft)
        if draft_request.draft_id:
            await db.execute(del_query)
        db.add_all(ques_list)
        await db.commit()
        await db.refresh(draft)

        return {
            ResponseKeys.MESSAGE: DRAFT_CREATED,
            ResponseKeys.DRAFT_ID: str(draft.id)
        }
        
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }


@router.delete(
    "/draft/{draft_id}"
)
async def delete_draft(
    request: Request,
    draft_id: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            draft = await db.get(PostDraft, draft_id)
            
            if not draft:
                raise Exception(DRAFT_NOT_FOUND)
            
            if draft.member_id != user.id:
                raise Exception(CANT_DELETE_DRAFT)

            if draft.type == PostType.Poll:
                del_query = delete(PollQues).where(PollQues.post_id == draft.id)
                await db.execute(del_query)
            
            await db.delete(draft)
            await db.commit()

            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }
            

@router.delete(
    "/post/{post_id}"
)
async def delete_post(
    request: Request,
    post_id: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            
            post = await db.get(Post, post_id)
            daily_ans = None
            if not post:
                daily_ans = await db.get(DailyAns, post_id)
                
            if post:
                if post.member_id != user.id:
                    raise Exception(CANT_DELETE_POST)
                
                _curr_status = await check_post_curr_details(db, post.id)[0]
                _curr_status.is_deleted = True
                _curr_status.update_at = current_datetime()
                
                _hist = await update_post_hist_to_deleted(db, _curr_status)
                
                
                if post.type == PostType.Question:
                    
                    _curr_ans_list, _hist_ans_list = await update_ans_posts_to_deleted(db, _curr_status)
                    
                    db.add_all(_curr_ans_list)
                    db.add_all(_hist_ans_list)
                    
                if post.type != PostType.Answer:
                    _params = {
                        "db": db,
                        "post_id": post.id,
                        "post_type": post.type
                    }
                    if post.type == PostType.Question:
                        _params["ans_ids"] = [ans.post_id for ans in _curr_ans_list]
                        
                    node_query, answer_query = await update_post_comments_to_deleted(**_params)
                    
                    db.add_all(node_query)
                    
                    if post.type == PostType.Question:
                        db.add_all(answer_query)
                    
                db.add(_curr_status)
                db.add(_hist)
                
            elif daily_ans:
                
                if daily_ans.member_id != user.id:
                    raise Exception(CANT_DELETE_POST)
                
                if daily_ans.is_deleted or daily_ans.is_blocked:
                    raise Exception(CANT_DELETE_POST)
                
                daily_ans.is_deleted = True
                daily_ans.update_at = current_datetime()
                db.add(daily_ans)
                
                
            else:
                raise Exception(POST_NOT_FOUND)
            

            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }
            

@router.delete(
    "/comment/{comment_id}"
)
async def delete_member_post(
    request: Request,
    comment_id: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():
        try:
            user: MemberProfileCurr = request.user
            
            comment = await db.get(CommentNode, comment_id)
            daily_comment = None
            if not comment:
                daily_comment = await db.get(DailyCommentNode, comment_id)
            
            if comment:
                
                if comment.member_id != user.id:
                    raise Exception(CANT_DELETE_COMMENT)
                if comment.is_deleted:
                    raise Exception(CANT_DELETE_COMMENT)
                
                comment.is_deleted = True
                comment.update_at = current_datetime()
                db.add(comment)
                
            elif daily_comment:
                
                if daily_comment.member_id != user.id:
                    raise Exception(CANT_DELETE_COMMENT)
                if daily_comment.is_deleted:
                    raise Exception(CANT_DELETE_COMMENT)
                
                daily_comment.is_deleted = True
                daily_comment.update_at = current_datetime()
                db.add(daily_comment)
            
            else:
                raise Exception(COMMENT_NOT_FOUND)

            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS
            }
        
        except Exception as exc:
            await db.rollback()
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }
            

@router.post(
    "/comment/{post_id}"
)
async def post_a_comment(
    request: Request,
    post_id: str,
    response: Response,
    comment: PostCommentRequest,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    async with db.begin():

        try:
            user: MemberProfileCurr = request.user
            
            if comment.post_type != PostType.Daily:
                post = await db.get(Post, post_id)
                if not post:
                    raise Exception(POST_NOT_FOUND)
                
            else:
                post = await db.get(DailyAns, post_id)
                if not post:
                    raise Exception(POST_NOT_FOUND)
                
            comment_id = await create_a_post_comment(db, post, comment, user.id)

            return {
                ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
                ResponseKeys.DATA: {
                    "comment_id": comment_id,
                    "member": {
                        "alias": user.alias,
                        "image": user.image,
                        "id": user.id
                    }
                }
            }

        except Exception as exc:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                ResponseKeys.MESSAGE: str(exc)
            }
        

@router.get(
    "/comment/{post_id}"
)
async def get_post_comments(
    request: Request,
    post_id: str,
    post_type: str,
    response: Response,
    Auth_token = Header(title=AuthTokenHeaderKey),
    db:AsyncSession = Depends(get_db),
):
    
    try:
        user: MemberProfileCurr = request.user

        if post_type != PostType.Daily:
            post = await db.get(Post, post_id)
            if not post:
                raise Exception(POST_NOT_FOUND)
            
        else:
            post = await db.get(DailyAns, post_id)
            if not post:
                raise Exception(POST_NOT_FOUND)
            
        
        return {
            ResponseKeys.MESSAGE: ResponseMsg.SUCCESS,
        }
            
    except Exception as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            ResponseKeys.MESSAGE: str(exc)
        }

        