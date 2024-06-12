import re
from uuid import UUID
from sqlalchemy import select, desc, text
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from unidecode import unidecode
from typing import List

from database.models import MemberProfileCurr, PollMemResult, PollMemReveal, PollMemTake, Post, PostStatusCurr, ViewPostScore
from utilities.constants import PaginationLimit, PostType

def unaccent(s):
    """
    Simulate the unaccent function.
    Replace accented characters with their non-accented equivalents.
    """
    # Define your own mapping or use a library for more comprehensive conversion
    accent_map = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'æ': 'ae', 'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i', 'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o', 'ø': 'o', 'œ': 'oe', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O', 'Œ': 'OE',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u', 'ü': 'u', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ç': 'c', 'Ç': 'C',
        'ð': 'd', 'Ð': 'D',
        '¿': '' , '¡': '' , 'ß': 'ss'
    }
    
    return ''.join(accent_map.get(char, char) for char in s)

def currency_unaccent(s):
    """
    Simulate the unaccent function.
    Replace accented characters with their non-accented equivalents.
    """
    currency_single_accent_map = {
        '$': '', '€': '', '£': '', '¥': '', '₹': '', '₽': '', '₩': '', '៛': '', '₡': '',
         '؋': '', 'Դ': '', 'ƒ': '', '₼': '', 
    "৳": "",
    "$": "",
    "৳": "",
    "€": "",
    "₣": "",
    "៛": "",
    "₡": "",
    "₱": "",
    "ƒ": "",
    "₱": "",
    "ლ": "",
    "﷼": "",
    "₪": "",
    "〒": "",
    "₭": "",
    "ރ": "",
    "₮": "",
    "₦": "",
    "₲": "",
    "₱": "",
    "ł": "",
    "₽": "",
    "₫": ""
}   
    currency_string_list = ["ب.د", 'د.ج', 'лв', "ع.د", "د.ا", "د.ك", "ل.ل", "ل.د", "د.م.", "ر.ع.","ر.ق", "ден"]
    
    cur_sing =  ''.join(currency_single_accent_map.get(char, char) for char in s)
    
    for i in currency_string_list:
        if i in cur_sing:
            cur_sing.replace(i, '')
            
    return cur_sing


def normalize_nickname(nickname):
    
    normalized_nickname = currency_unaccent(nickname)
    
    normalized_nickname = unidecode(normalized_nickname)
    
    # Remove accents
    normalized_nickname = unaccent(normalized_nickname)
    
    # pattern = re.compile(r'[^a-zA-Z\s]')
    
    # if pattern.search(normalized_nickname):
    #     raise
    
    # Replace non-whitespace characters with a single space
    normalized_nickname = re.sub(r'[^a-zA-Z\s]', ' ', normalized_nickname)
    
    # Replace sequences of whitespace characters with a single space
    normalized_nickname = re.sub(r'\s+', ' ', normalized_nickname)
    
    # Trim leading and trailing whitespace
    normalized_nickname = normalized_nickname.strip()
    
    # Convert to uppercase
    normalized_nickname = normalized_nickname.upper()
    
    return normalized_nickname

"""
nickname = "kožušček José  @%$ García 12421 \n icwbb kožušček 21321 $*#^@* ä, ë, ï, ö, ü, ÿ, Ä, Ë, Ï, Ö, Ü, Ÿ, œ, Œ, æ, Æ, ø, Ø, ¿, ¡, ß, å, Å"


vad = unidecode(nickname)
normalized_nickname = normalize_nickname(vad)
print(normalized_nickname)

vad = unidecode('kožušček 21321 $*#^@* ä, ë, ï, ö, ü, ÿ, Ä, Ë, Ï, Ö, Ü, Ÿ, œ, Œ, æ, Æ, ø, Ø, ¿, ¡, ß, å, Å')
"""

most_popular_base_query = (
    select(ViewPostScore, Post, PostStatusCurr, MemberProfileCurr.image, MemberProfileCurr.alias)
    .join(Post, Post.id == ViewPostScore.post_id)
    .join(PostStatusCurr, PostStatusCurr.post_id == ViewPostScore.post_id)
    .join(MemberProfileCurr, Post.member_id == MemberProfileCurr.id)
)

async def get_most_popular_base_func(
    conditions: dict = {}, 
):
    query = most_popular_base_query
    for table_column, value in conditions.items():
        table, column = table_column.split(".")
        mapped_table = globals()[table]
        query = query.where(getattr(mapped_table, column) == value)

    return query

async def get_random_sample_questions_polls(session: AsyncSession, sample_size: int, post_type: str) -> List[Post]:

    stmt = text(f"""
        SELECT * 
        FROM pst.post_posted 
        TABLESAMPLE SYSTEM(:sample_size) 
        WHERE post_posted.post_type = :post_type
    """)
    result = await session.execute(stmt, {'sample_size': sample_size, 'post_type': post_type})
    return result.scalars().all()

async def get_random_questions_polls_with_details(
    session: AsyncSession, 
    sample_size: int,
    post_type: str,
    member_id: UUID
) -> List:
    
    random_sample_posts = await get_random_sample_questions_polls(session, sample_size, post_type)

    if not random_sample_posts:
        return []
    
    remove_post_ids = []
    
    if post_type == PostType.Answer:
        answered_post_ids_query = (
            select(Post.assc_post_id)
            .where(
                Post.member_id == member_id,
                Post.type == post_type,
            )
        )
        results = await session.execute(answered_post_ids_query)
        answered_post_ids = results.fetchall()
        answered_post_ids = [i[0] for i in answered_post_ids]
        
        remove_post_ids.extend(answered_post_ids)
        
    elif post_type == PostType.Poll:
        
        taken_polls_query = (
            select(PollMemTake.post_id)
            .where(
                PollMemTake.member_id == member_id,
            )
        )
        
        results = await session.execute(taken_polls_query)
        poll_selected = results.fetchall()
        poll_selected = [i[0] for i in poll_selected]
        remove_post_ids.extend(poll_selected)
        
        reveal_polls_query = (
            select(PollMemReveal.post_id)
            .where(
                PollMemReveal.member_id == member_id,
            )
        )
        results = await session.execute(reveal_polls_query)
        reveal_selected = results.fetchall()
        reveal_selected = [i[0] for i in reveal_selected]
        remove_post_ids.extend(reveal_selected)      
        
    
    PostStatusCurrAlias = aliased(PostStatusCurr)
    MemberProfileCurrAlias = aliased(MemberProfileCurr)
    
    stmt = (
        select(Post, PostStatusCurrAlias, MemberProfileCurrAlias.image, MemberProfileCurrAlias.alias)
        .join(PostStatusCurrAlias, Post.id == PostStatusCurrAlias.post_id)
        .join(MemberProfileCurrAlias, Post.member_id == MemberProfileCurrAlias.id)
        .where(
            Post.id.in_(random_sample_posts),
            PostStatusCurrAlias.is_blocked == False,
            PostStatusCurrAlias.is_deleted == False,
            Post.id.notin_(remove_post_ids),
        )
    )
    
    result = await session.execute(stmt)
    return result.all()




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