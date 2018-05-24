# -*- coding: utf-8 -*-

import oss2

from configs.config import *


def put_file_to_oss(filename, data):
    """For YouWenBiDa QRcode img."""

    auth = oss2.Auth(OSS_KEY, OSS_SECRET)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, BUCKET_NAME)
    bucket.put_object(filename, data)

    return 'http://' + BUCKET_NAME + '.' + OSS_ENDPOINT + '/' + filename
