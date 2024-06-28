url = "https://api.unsplash.com/photos/random"

import requests
import json

# """
uns = requests.get(
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
    file.write(json.dumps(uns.json()))
# """

"""
down = requests.get(
    "https://unsplash.com/photos/YpSr2YJSuUY/download?ixid=M3w2Mjc0NzJ8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MTk1MTYzNjF8",
    headers={
        "Authorization": "Client-ID BmoLfkv_DDjaLWpskJ4ANXf0wREe_N5rFfJlu5mDWAg",
    }
)


if down.status_code == 200:
    with open("downloaded_image.jpg", "wb") as file:
        file.write(down.content)
else:
    print("Failed to download image. Status code:", down.status_code)

"""
