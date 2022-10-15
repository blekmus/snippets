from hashlib import sha256
import json
import subprocess
import logging
from rich.text import Text
from datetime import datetime
from rich.console import Console
import os
from tusclient import client
import requests

save_loc = "../volume"
testing = True

logging.basicConfig(level=logging.DEBUG,
                    datefmt="%I:%M:%S",
                    format="[%(asctime)s] %(levelname)s: %(message)s",
                    filename='./script.log',
                    filemode="a")


def logger(msg, level='info'):
    if level != 'debug':
        timestamp = datetime.now().strftime("%I:%M:%S")

        console = Console()
        console.print(f"[{timestamp}]", end=" ")
        console.print(f"{msg}", highlight=False)

    msg = Text().from_markup(msg)

    if level == 'debug':
        logging.debug(msg)
    elif level == 'warning':
        logging.warning(msg)
    elif level == 'error':
        logging.error(msg)
    else:
        logging.info(msg)


def run_shell(shell_command):
    with open('script.log', "a") as outfile:
        subprocess.run(shell_command,
                       shell=True,
                       stdout=outfile,
                       stderr=outfile,
                       check=True)


def set_failed(video):
    with open('./failed.json', 'r') as file:
        failed = json.load(file)

    failed.append(video)

    with open('./failed.json', 'w') as file:
        json.dump(failed, file, indent=4)


def set_current(current_video):
    with open('./current.txt', 'w') as file:
        file.write(str(current_video))


def download_video(video, filename):
    dl_command = f"yt-dlp \"{video['url']}\" -o \"{filename}\" --referer \"https://aceacademy.lk\""

    logger("Running [blue]yt-dlp...[/blue]")
    logger(dl_command, level='debug')

    try:
        run_shell(dl_command)
        logger("Successfully downloaded")
        return True
    except Exception:
        logger("[bold red]Download failed[/bold red]", level='error')
        return False


def b2_upload(filename):
    up_command = f"rclone copy \"{filename}\" b2:ace-academy-recordings/archive/ -vvv"

    logger("Running [blue]rclone..[/blue].")
    logger(up_command, level='debug')

    try:
        run_shell(up_command)
        logger("Successfully uploaded to b2")
        return True
    except Exception:
        logger("[bold red]b2 Upload failed[/bold red]", level='error')
        return False


def bunny_upload(filename, title):
    logger("Running [blue]bunny[/blue]...")

    library_id = '63177'
    api_key = '0f1lkjsdlksj4a99'
    collection_id = 'flkjasdflkasj-oqiwpurpoi4u2'

    url = f"https://video.bunnycdn.com/library/{library_id}/videos"

    headers = {
        "accept": "application/json",
        "content-type": "application/*+json",
        "AccessKey": api_key,
    }

    payload = {
        'title': filename,
        'collectionId': collection_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    created_video = response.json()

    logger(response.text, level='debug')

    tus_uploader = client.TusClient('https://video.bunnycdn.com/tusupload')

    expires = int(datetime.now().timestamp()) + 3600
    signature = sha256((library_id + api_key + str(expires) + created_video['guid']).encode('utf-8')).hexdigest()
    tus_uploader.set_headers({'AuthorizationSignature': signature})
    tus_uploader.set_headers({'AuthorizationExpire': str(expires)})
    tus_uploader.set_headers({'VideoId': created_video['guid']})
    tus_uploader.set_headers({'LibraryId': library_id})

    metadata = {
        'filetype': 'mp4',
        'title': title,
    }

    uploader = tus_uploader.uploader(filename, metadata=metadata,)

    try:
        uploader.upload()
        logger("Successfully uploaded to bunny\n")
        return "https://iframe.mediadelivery.net/embed/" + library_id + created_video['guid']
    except Exception:
        logger("[bold red]Bunny Upload failed[/bold red]\n", level='error')
        return False


def update_ace(video):
    pass


def main():
    if testing:
        with open('failed.json', 'w') as file:
            json.dump([], file, indent=4)

        with open('current.txt', 'w') as file:
            file.write("0")

        with open('script.log', 'w') as file:
            file.write("")

        with open('completed.json', 'w') as file:
            file.write("")

    # get all videos
    with open('./videos.json', 'r') as file:
        data = json.load(file)

    # get current video index
    with open('./current.txt', 'r') as file:
        current_video = int(file.read())

    # slice data and get videos after current_video
    videos = data[current_video:]
    completed_videos = []

    for video in videos:
        logger(
            f"Running on\n[bold]Lesson ID: [/bold][blue]{video['lesson_id']}[/blue]\n[bold]Lesson Title: [/bold][blue]{video['title']}[/blue]\n[bold]Course ID: [/bold][blue]{video['course_id']}[/blue]\n[bold]Course Title: [/bold][blue]{video['course_title']}[/blue]\n[bold]URL: [/bold][blue]{video['url']}[/blue]"
        )

        title = f"{video['title']} |||| {video['lesson_id']} |||| {video['course_title']} |||| {video['course_id']}"
        filename = f"{save_loc}/{title} ||||.mp4"
        logger(filename, level='debug')

        # download video using yt-dlp
        download_status = download_video(video, filename)
        if not download_status:
            set_failed(video)
            set_current(current_video + 1)
            continue

        # upload video to backblaze using rclone
        b2_status = b2_upload(filename)
        if not b2_status:
            set_failed(video)
            set_current(current_video + 1)
            continue

        # upload video to bunny stream
        bunny_status = bunny_upload(filename, title)
        if not bunny_status:
            set_failed(video)
            set_current(current_video + 1)
            continue

        # save bunny stream url to video
        video['bunny_url'] = bunny_status

        # send new url to ace academy
        update_ace(video)

        completed_videos.append(video)
        set_current(current_video + 1)

        # delete video from local
        os.remove(filename)

    # save completed videos to json
    with open('./completed.json', 'w') as file:
        json.dump(completed_videos, file, indent=4)


main()
