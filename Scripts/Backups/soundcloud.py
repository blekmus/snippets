import subprocess
import tempfile
import requests

# create temp dir
with tempfile.TemporaryDirectory() as tempdirname:
    print("started")

    # send start ping to healthcheck
    requests.get(
        'https://hc-ping.com/e3e321d1-f780-4730-a146-sadfsdfsfsdf/start')

    # download songs from soundcloud
    subprocess.run(
        f"yt-dlp --embed-thumbnail --embed-metadata -P {tempdirname} https://soundcloud.com/blekmus/likes",
        shell=True,
        check=True)

    # copy files to backblaze
    subprocess.run(
        f"rclone copy {tempdirname}/ b2-backup:caiden-backups/SoundCloud/ -vvv",
        shell=True,
        check=True)

    # send success ping to healthcheck
    requests.get('https://hc-ping.com/e3e321d1-f780-4730-a146-34c4345x34')

    print("done")
