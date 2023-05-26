import boto3
import yaml

import util


def assert_has_field(profile, field):
    util.assert_with_actions(field in profile, f"ERROR: Expected '{field}' in profile '{profile['name']}'")


class Uploader:
        def __init__(self, profile):
            assert_has_field(profile, 'aws_access_key_id')
            assert_has_field(profile, 'aws_secret_access_key')
            assert_has_field(profile, 's3_bucket')

            session = boto3.session.Session()
            self._s3 = session.client(
                service_name='s3',
                endpoint_url='https://storage.yandexcloud.net',
                aws_access_key_id=profile['aws_access_key_id'],
                aws_secret_access_key=profile['aws_secret_access_key'],
            )
            self._bucket = profile['s3_bucket']

        def is_exist(self, name):
            try:
                self._s3.get_object(Bucket=self._bucket, Key=name)
                return True
            except:
                return False

        def upload(self, path, name):
            self._s3.upload_file(path, self._bucket, name)


def get_code_uploader_client():
    profiles = util.load_profiles()
    return Uploader(profiles['code-uploader'])
