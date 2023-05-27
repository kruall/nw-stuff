import boto3

import core.util as util


def assert_has_field(profile, field):
    util.assert_with_actions(field in profile, f"ERROR: Expected '{field}' in profile '{profile['name']}'")


def assert_s3_profile(profile):
    assert_has_field(profile, 'aws_access_key_id')
    assert_has_field(profile, 'aws_secret_access_key')
    assert_has_field(profile, 's3_bucket')


class ProfiledObject:
    def __init__(self, profile):
        assert_s3_profile(profile)
        self._profile = profile

        self._session = boto3.session.Session()
        self._s3 = self._session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=profile['aws_access_key_id'],
            aws_secret_access_key=profile['aws_secret_access_key'],
        )
        self._bucket = profile['s3_bucket']


class Watcher(ProfiledObject):
    def __init__(self, profile):
        ProfiledObject.__init__(self, profile)

    def is_exist(self, name):
        try:
            self._s3.get_object(Bucket=self._bucket, Key=name)
            return True
        except:
            return False

    def list(self):
        return [key['Key'] for key in self._s3.list_objects(Bucket=self._bucket).get('Contents', [])]


class Uploader(Watcher):
    def __init__(self, profile):
        Watcher.__init__(self, profile)

    def upload(self, path, name):
        self._s3.upload_file(path, self._bucket, name)

    def write(self, name, file):
        try:
            object = self._s3.get_object(Bucket=self._bucket, Key=name)
        except:
            raise util.HaltError("Can't get object")
        file.write(object['Body'].read())

    def download(self, name, path):
        try:
            object = self._s3.get_object(Bucket=self._bucket, Key=name)
        except:
            raise util.HaltError("Can't get object")
        util.validate_path_unexistence(path, f"Can't download '{name}' because {path} already exist")
        with open(path, 'wb') as file:
            file.write(object['Body'].read())


def get_code_uploader_client():
    return Uploader(util.get_profile('code-uploader'))


def get_file_uploader_client():
    return Uploader(util.get_profile('file-share'))
