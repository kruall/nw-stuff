import boto3
import sys
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)
s3.upload_file(sys.argv[1], 'model-storage', sys.argv[1])