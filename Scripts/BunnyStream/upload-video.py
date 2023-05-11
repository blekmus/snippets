import argparse
import hashlib
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from slugify import slugify

import requests
from tusclient import client

load_dotenv()

def upload_video(filename):
    title = slugify(filename)
    library_id = os.environ["BUNNY_LIBRARY_ID"]
    api_key = os.environ["BUNNY_API_KEY"]
    collection_id = os.environ["BUNNY_COLLECTION_ID"]

    url = f"https://video.bunnycdn.com/library/{library_id}/videos"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "AccessKey": api_key,
    }

    payload = {
        'title': title,
        'collectionId': collection_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    created_video = response.json()

    tus_uploader = client.TusClient('https://video.bunnycdn.com/tusupload')

    expires = int(datetime.now().timestamp()) + 3600
    signature = hashlib.sha256((library_id + api_key + str(expires) + created_video['guid']).encode('utf-8')).hexdigest()
    tus_uploader.set_headers({'AuthorizationSignature': signature})
    tus_uploader.set_headers({'AuthorizationExpire': str(expires)})
    tus_uploader.set_headers({'VideoId': created_video['guid']})
    tus_uploader.set_headers({'LibraryId': library_id})

    metadata = {
        'filetype': 'mkv',
        'title': title,
    }

    uploader = tus_uploader.uploader(filename, metadata=metadata, chunk_size=1024 * 1024 * 40)
    uploader.upload()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a video file to BunnyCDN")
    parser.add_argument("filename", type=str, help="The path to the video file")
    args = parser.parse_args()

    upload_video(args.filename)
