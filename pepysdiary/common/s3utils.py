from storages.backends.s3boto import S3BotoStorage
# from django.utils.functional import SimpleLazyObject

StaticS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaS3BotoStorage = lambda: S3BotoStorage(location='media')
