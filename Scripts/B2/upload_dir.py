from b2sdk.v2 import *
import sys
import time


def upload_dir():
    keyID = 'key'
    appKey = 'key'
    bucket = 'bucket-name'
    source_path = '/path/to/dir'
    dest_path = '/path/in/bucket'

    # init b2
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", keyID, appKey)

    # setup upload info
    file_info = {'how', 'good-file'}
    bucket = b2_api.get_bucket_by_name(bucket)

    # resolve source and dest
    source = parse_sync_folder(source_path, b2_api)
    destination = parse_sync_folder(f'b2://{bucket}/{dest_path}', b2_api)

    # init uploader
    synchronizer = Synchronizer(max_workers=5)

    # upload files
    with SyncReport(sys.stdout, True) as report:
        synchronizer.sync_folders(source_folder=source,
                                  dest_folder=destination,
                                  now_millis=int(round(time.time() * 1000)),
                                  reporter=report)
