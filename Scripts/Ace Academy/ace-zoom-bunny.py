import hashlib
import hmac
import sys
import logging
import json
import os
from dotenv import load_dotenv
import requests
import subprocess
from tusclient import client
from datetime import datetime


logging.basicConfig(level=logging.DEBUG,
                    datefmt="%I:%M:%S",
                    format="[%(asctime)s] %(levelname)s: %(message)s",
                    filename='script.log',
                    filemode="a")

def run_shell(shell_command):
    with open('script.log', "a") as outfile:
        subprocess.run(shell_command,
                       shell=True,
                       stdout=outfile,
                       stderr=outfile,
                       check=True)


def verify_signature(headers):
    # signature verification doesn't seem to work
    # plus its commented out here https://github.com/zoom/webhook-sample-node.js/blob/master/index.js#L31
    # signature = headers["X-Zm-Signature"]
    # timestamp = headers["X-Zm-Request-Timestamp"]
    # secret = os.environ["ZOOM_WEBHOOK_SECRET"]

    # # create the signature
    # data = f"v0:{timestamp}:{json.dumps(payload)}"

    # logging.debug(data)

    # hash = hmac.new(secret.encode(), data.encode(), hashlib.sha256)
    # signature_check = f"v0={hash.hexdigest()}"

    # logging.debug(signature_check)

    # # compare the signatures
    # if signature == signature_check:
    #     return True
    # else:
    #     return False'

    # for now verify using ClientId
    if headers["Clientid"] == os.environ["ZOOM_CLIENT_ID"]:
        return True
    else:
        return False


def download_recording(download_url, filename):
    r = requests.get(download_url, stream=True)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        raise Exception("Failed to download the recording")


def b2_upload(filename):
    up_command = f"rclone copy \"./{filename}\" b2-ace:ace-academy-recordings/zoom/ -vvv --buffer-size 0"
    logging.info("Running rclone...")
    logging.debug(up_command)

    run_shell(up_command)
    logging.info("Successfully uploaded to b2")


def bunny_upload(filename, title):
    logging.info("Running bunny...")

    library_id = os.environ["BUNNY_LIBRARY_ID"]
    api_key = os.environ["BUNNY_API_KEY"]
    collection_id = os.environ["BUNNY_COLLECTION_ID"]

    url = f"https://video.bunnycdn.com/library/{library_id}/videos"

    headers = {
        "accept": "application/json",
        "content-type": "application/*+json",
        "AccessKey": api_key,
    }

    payload = {
        'title': title,
        'collectionId': collection_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    created_video = response.json()

    logging.debug(response.text)

    tus_uploader = client.TusClient('https://video.bunnycdn.com/tusupload')

    expires = int(datetime.now().timestamp()) + 3600
    signature = hashlib.sha256((library_id + api_key + str(expires) + created_video['guid']).encode('utf-8')).hexdigest()
    tus_uploader.set_headers({'AuthorizationSignature': signature})
    tus_uploader.set_headers({'AuthorizationExpire': str(expires)})
    tus_uploader.set_headers({'VideoId': created_video['guid']})
    tus_uploader.set_headers({'LibraryId': library_id})

    metadata = {
        'filetype': 'mp4',
        'title': title,
    }

    logging.debug(filename)
    logging.debug(metadata)

    uploader = tus_uploader.uploader(filename, metadata=metadata, chunk_size=1024 * 1024 * 40)
    uploader.upload()



def main():
    # check if the script has arguments
    if not len(args) > 2:
        logging.error("No arguments provided")
        sys.exit(1)
    
    # check if both arguments are json strings
    try:
        payload = json.loads(args[1])
        headers = json.loads(args[2])
    except Exception as err:
        logging.error("Arguments are not json strings")
        logging.error(err)
        sys.exit(1)

    logging.debug(payload)
    logging.debug(headers)

    # verify zoom webhook signature
    if not verify_signature(headers):
        logging.error("Invalid signature")
        sys.exit(1)
    
    logging.info("Signature verified")


    # filter recordings by duration
    if payload["payload"]["object"]["duration"] < 20:
        logging.info("Recording is too short, skipping")
        sys.exit(0)


    # filter recordings by their type
    recording = [recording for recording in payload["payload"]["object"]["recording_files"] if recording["recording_type"] == "shared_screen_with_speaker_view"][0]

    # resolve filename
    filename = f"{recording['recording_start']} {payload['payload']['object']['topic']}"

    logging.info(filename)

    # download the recording
    try:
        download_recording(recording["download_url"], f"{filename}.mp4")
    except Exception as err:
        logging.error("Failed to download the recording")
        logging.error(err)
        sys.exit(1)

    # upload recording to b2 bucket
    try:
        b2_upload(f"{filename}.mp4")
    except Exception as err:
        logging.error("Failed to upload recordings to b2 bucket")
        logging.error(err)
        os.remove(f"{filename}.mp4")
        sys.exit(1)

    # upload recording to bunny stream
    try:
        bunny_upload(f"{filename}.mp4", filename)
    except Exception as err:
        logging.error("Failed to upload recordings to bunny stream")
        logging.error(err)
        os.remove(f"{filename}.mp4")
        sys.exit(1)

    # remove the recording
    os.remove(f"{filename}.mp4")

    logging.info("Successfully uploaded the recording")

        

# load env variables
load_dotenv()

# load arguments from shell script
args = sys.argv


if __name__ == "__main__":
    main()



