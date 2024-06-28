url = "https://api.unsplash.com/photos/random"

import requests
import json
import redis
import boto3, os

REDIS_DB = S3_ACCESS_KEY_ID = S3_BUCKET_NAME = S3_REGION = S3_SECRET_ACCESS_KEY = 0

CLOUDFRONT_URL = ""

def upload_file(file, name):
    
    try:
        s3_client = boto3.client(
            's3',
            region_name= S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY
        )
        
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, name)
        return True
    except Exception as e:
        print("Exception file not uploaded: ", str(e))
        return False

def remove_file(file):
    try:
        s3_client = boto3.client(
            's3',
            region_name= S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY
        )
        
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file)
        return True
    except Exception as e:
        print("Exception file not deleted: ", str(e))
        return False

rd = redis.Redis(db = REDIS_DB)



def fetch_random_images(count=5):
    response = requests.get(
        "https://api.unsplash.com/photos/random",
        params={
            "orientation": "landscape",
            "count": count
        },
        headers={
            "Authorization": "Client-ID BmoLfkv_DDjaLWpskJ4ANXf0wREe_N5rFfJlu5mDWAg",
            "Accept-Version": "v1",
        }
    )
    response.raise_for_status()
    return response.json()


def save_image_locally(image_data, index):
    
    img_data = requests.get(
        image_data['links']['download'],
        headers={
            "Authorization": "Client-ID YOUR_UNSPLASH_ACCESS_KEY",
        }
    )
    
    img_data.raise_for_status()
    
    file_path = f"downloaded_image_{index}.jpg"
    with open(file_path, "wb") as file:
        file.write(img_data.content)
    return file_path


def main():
    rd = redis.Redis(db=REDIS_DB)
    rd.delete('image_ids')  # Clear the Redis key before adding new image IDs

    data = fetch_random_images()

    with open("image_ids.txt", 'w') as file:
        for i, image in enumerate(data):
            image_id = image['id']
            
            if i==0:
                file.truncate(0)
                
            file.write(f"{image_id}\n")
            
            CLOUDFRONT_URL + image_id
            
            rd.rpush('image_ids', image_id)
            
            
            file_path = save_image_locally(image, i)
            # remove_file(file_path)
            # upload_file(file_path, image_id)
            # os.remove(file_path)
    
    rd.close()


if __name__ == "__main__":
    main()





"""
response = requests.get(
    "https://api.unsplash.com/photos/random",
    params={
      "orientation": "landscape",  
      "count": 5
    },
    headers={
        "Authorization": "Client-ID BmoLfkv_DDjaLWpskJ4ANXf0wREe_N5rFfJlu5mDWAg",
        "Accept-Version": "v1",
    }
)
with open("res.json", 'w') as file:
    file.write(json.dumps(response.json()))

data = response.json()

for i, image in enumerate(data):
    
    ID = image['id']
    with open("image_ids.txt", 'a') as file:
        if i == 0:
            file.truncate(0)
            rd.delete('image_ids')
        file.write(f"{ID}\n")
        
    
    _link = image['links']['download']
    
    img_data = requests.get(
        _link,
        headers={
            "Authorization": "Client-ID BmoLfkv_DDjaLWpskJ4ANXf0wREe_N5rFfJlu5mDWAg",
        }
    )
        
    if img_data.status_code == 200:
        with open(f"downloaded_image_{i}.jpg", "wb") as file:
            file.write(img_data.content)
            
        #also set image in redis
        upload_file(file, ID)

rd.close()


"""
