from storages.backends.s3boto3 import S3Boto3Storage


class MediaS3Boto3Storage(S3Boto3Storage):
    # Store files under "media/" directory in the bucket:
    location = "media"
