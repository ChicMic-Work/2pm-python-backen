import boto3
import botocore.client
from botocore.config import Config
from botocore.exceptions import ClientError

from utilities.constants import(
    UPLOAD_TO_S3,
    S3_BUCKET_NAME,
    CLOUDFRONT_URL,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    S3_REGION
)


s3_client = boto3.client(
    's3',
    region_name= S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY_ID,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY
    )

def upload_file(file, name):
    
    try:
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, name)
        return True
    except Exception as e:
        print("Exception file not uploaded: ", str(e))
        return False
    
    


def remove_file(file):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file)
        return True
    except Exception as e:
        print("Exception file not deleted: ", str(e))
        return False

