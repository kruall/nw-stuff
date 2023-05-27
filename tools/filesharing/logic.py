import os

import core.object_storage as object_storage
import core.util as util


def upload_file(path, name):
    uploader = object_storage.get_file_uploader_client()
    util.assert_with_actions(not uploader.is_exist(name), f"ERROR: File with '{name}' name  alreade exists")
    uploader.upload(path, name)


def list_of_files():
    uploader = object_storage.get_file_uploader_client()
    return uploader.list()


def download_file(name, path):
    uploader = object_storage.get_file_uploader_client()
    uploader.download(name, path)


def download_files(names, path):
    uploader = object_storage.get_file_uploader_client()
    for name in names:
        file_path = os.path.join(path, name)
        uploader.download(name, file_path)


def write_file(name, file):
    uploader = object_storage.get_file_uploader_client()
    uploader.write(name, file)
