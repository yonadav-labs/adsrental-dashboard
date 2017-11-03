
from storages.backends.s3boto import S3BotoStorage


def StaticRootS3BotoStorage():
    return S3BotoStorage(location='static')
