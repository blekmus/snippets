from b2sdk.v2 import *
import sys
import time


def upload_file():
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

    # upload and get download url
    uploaded = bucket.upload_local_file(source_path,
                                        dest_path,
                                        file_infos=file_info)

    # file download url
    download = b2_api.get_download_url_for_fileid(uploaded.id_)
    print(download)