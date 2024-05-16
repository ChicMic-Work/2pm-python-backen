import pytz, os
from dotenv import load_dotenv

from datetime import datetime, timedelta

load_dotenv()
SECRET_KEY  = os.getenv("SECRET_KEY")
ALGORITHM   = os.getenv("ALGORITHM")

EMAIL_HOST          = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT          = os.getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL")

APPLE_TOKEN_ISS     = os.getenv("APPLE_TOKEN_ISS")
APPLE_TOKEN_AUD     = os.getenv("APPLE_TOKEN_AUD")
APPLE_AUTH_KEY_URL  = os.getenv("APPLE_AUTH_KEY_URL")
GOOGLE_TOKEN_AUD    = os.getenv("GOOGLE_TOKEN_AUD")
GOOGLE_AUTH_KEY_URL = os.getenv("GOOGLE_AUTH_KEY_URL")

#S3
UPLOAD_TO_S3    = os.getenv("UPLOAD_TO_S3")
S3_BUCKET_NAME  = os.getenv("S3_BUCKET_NAME")
CLOUDFRONT_URL  = os.getenv("CLOUDFRONT_URL")
S3_REGION       = os.getenv("S3_REGION")
S3_ACCESS_KEY_ID        = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY    = os.getenv("S3_SECRET_ACCESS_KEY")


current_time = datetime.now() 
access_token_expire = timedelta(days=30)

AuthTokenHeaderKey = "Auth-Token"
protected_endpoints = [
    '/tr', '/profile/create/', '/profile/alias', '/profile/image/', '/profile/user'
]

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
    
ALIAS_VALID     = "Valid"
ALIAS_INVALID   = "Invalid"
ALIAS_EXISTS    = "Nickname Already Exists"
ALIAS_CURRENT   = "Current"
ALIAS_INVALID_CHARACTER = "Nickname should not contain special characters and numbers"

IMAGE_FAIL = "Failed to save image"

"""
TIMEZONE = 'Asia/Kolkata' pytz.timezone(TIMEZONE)
"""