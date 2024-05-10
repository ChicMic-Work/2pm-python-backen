import pytz, os
from dotenv import load_dotenv

from datetime import datetime, timedelta

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# TIMEZONE = 'Asia/Kolkata' pytz.timezone(TIMEZONE)
current_time = datetime.now() 
access_token_expire = timedelta(hours=6)

AuthTokenHeaderKey = "Auth-Token"
protected_endpoints = ['/tr', '/profile/create']

class SocialType:
    Google = 0
    Apple = 1
    
class ChoicesType:
    Interest_Area = 0
    Language = 1
    
class PromoType:
    T = "Free Trial"
    S = "Fee Waiver"
    M = "Manual"