from database.models import MemberProfile
from sqlalchemy.event import listens_for
from sqlalchemy.sql import func


# @listens_for(MemberProfile, "before_update")
# def receive_before_update(mapper, connection, target):
#     target.updated_at = current_time