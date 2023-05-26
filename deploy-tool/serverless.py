import os
import json
import sys
import argparse
import shutil
import hashlib
import zipfile
import glob

import util
import shell
import object_storage

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def validate_dir_existence(path, extra_msg=None):
    util.assert_with_actions(os.path.isdir(path), f"ERROR: Expected directory '{path}'.", extra_msg=extra_msg)


def validate_file_existence(path, extra_msg=None):
    util.assert_with_actions(os.path.isfile(path), f"ERROR: Expected file '{path}'.", extra_msg=extra_msg)


def validate_path_unexistence(path, extra_msg=None):
    util.assert_with_actions(not os.path.exists(path), f"ERROR: Unexpected existence '{path}'.", extra_msg=extra_msg)


def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


class LocalServerlessFunction:
    def __init__(self, project, name):
        self._project = project
        self._name = name
        self.project_path = os.path.join(util.code_path, project)
        self.function_path = os.path.join(self.project_path, 'serverless', name)
        self.config_path = os.path.join(self.function_path, 'config.yaml')

        self._config = None
        self._code_hash = None
        self._archive_name = None

    def get_config(self):
        if self._config is None:
            with open(self.config_path, 'r') as file:
                self._config = yaml.load(file, Loader=Loader)
            if 'entrypoint' in self._config:
                entrypoint = self._config['entrypoint']
                rel_path = os.path.relpath(self.function_path, util.code_path)
                print(rel_path)
                self._config['entrypoint'] = f'{str(rel_path).replace("/", ".")}.{entrypoint}'
        return self._config

    def validate_config(self):
        config = self.get_config()
        fields = set(config.keys())

        field_types = {
            'entrypoint': str,
            'runtime': str,
            'memory': str,
            'execution-timeout': str,
            'description': str,
            'environment': str,
            'tags': str,
            'secret': list
        }
        required_fields = {'entrypoint', 'runtime'}
        optional_fields = set(field_types.keys()).difference(required_fields)

        unexpected_fields = fields.difference(required_fields, optional_fields)
        unexisted_required_fields = required_fields.difference(fields)

        util.assert_with_actions(not unexpected_fields, f"ERROR: Unexpected fields in the config: {list(sorted(unexpected_fields))}")
        util.assert_with_actions(not unexisted_required_fields, f"ERROR: Expected next fields in the config: {list(sorted(unexisted_required_fields))}")

        for field_name, value in config.items():
            expected_type = field_types[field_name]
            util.assert_with_actions(isinstance(value, expected_type), f"ERROR: Unexpected type '{type(value)}' of field '{field_name}', expected '{expected_type}")

    def validate_for_update(self):
        validate_path_unexistence(util.out_path, extra_msg="Can't update function with existed 'out' directory. Complete previous operation.")
        validate_dir_existence(util.code_path, extra_msg="Can't update function without code directory.")
        validate_dir_existence(self.function_path, extra_msg="Can't update function without serverless directory.")
        validate_file_existence(self.config_path, extra_msg="Can't update function without config.json.")
        self.validate_config()

    def validate_for_creation(self):
        validate_dir_existence(util.code_path, extra_msg="Can't create function without code directory.")
        validate_dir_existence(self.function_path, extra_msg="Can't create function without serverless directory.")
        validate_file_existence(self.config_path, extra_msg="Can't create function without config.json.")
        self.validate_config()

    def generate_yc_update_arguments(self):
        config = self.get_config()

        arguments = []
        for field_name, value in config.items():
            if isinstance(value, str):
                arguments.append(f"--{field_name}={value}")
            if isinstance(value, list):
                for line in value:
                    arguments.append(f"--{field_name}={line}")

        arguments.append(f'--function-name={self._name}')
        arguments.append(f'--package-bucket-name={self._bucket}')
        arguments.append(f'--package-object-name={self._archive_name}')
        arguments.append(f'--package-sha256={self._code_hash}')
        return arguments

    def generate_yc_create_arguments(self):
        config = self.get_config()

        arguments = []
        arguments.append(f'--name={self._name}')
        if 'description' in config:
            arguments.append(f'--description={config["description"]}')
        if 'labels' in config:
            kv_strings = (f'{k}:{v}' for k, v in config['labels'])
            arguments.append(f'--labels={",".join(kv_strings)}')
        return arguments

    def _make_archive(self, archive_path):
        shutil.copytree(util.code_path, util.out_code_path)
        with zipfile.ZipFile(archive_path, 'w') as archive:
            pattern = os.path.join(util.out_code_path, '**')

            for file in glob.glob(pattern, recursive=True):
                if '.pyc' in file or '__pycache__' in file:
                    continue
                if os.path.isfile(file):
                    relpath = os.path.relpath(file, util.out_code_path)
                    archive.write(file, relpath)

    def _upload_archive(self, archive_path):
        self._code_hash = sha256sum(archive_path)
        self._archive_name = f'code-{self._code_hash[-6:]}.zip'

        code_uploader = object_storage.get_code_uploader_client()
        self._bucket = code_uploader._bucket
        if not code_uploader.is_exist(self._archive_name):
            code_uploader.upload(archive_path, self._archive_name)

    def upload_code(self):
        os.makedirs(util.out_path)
        try:
            archive_path = os.path.join(util.out_path, 'code.zip')
            self._make_archive(archive_path)
            self._upload_archive(archive_path)
        except:
            shutil.rmtree(util.out_path)
            raise
        else:
            shutil.rmtree(util.out_path)
            return self._code_hash


def get_list_of_serverless_functions():
    cmd = 'yc serverless function list --format=json'
    proc = shell.run(cmd)
    if proc.return_code != 0:
        print(f"ERROR: command failed '{cmd}'", file=sys.stderr)
        print(f"{proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout)


def delete_serverless_function(name):
    cmd = f"yc serverless function delete --name='{name}'"
    proc = shell.run(cmd)
    if proc.return_code == 0:
        print('success')
    else:
        print(f"ERROR: command failed '{cmd}'", file=sys.stderr)
        print(f"{proc.stderr}", file=sys.stderr)
        sys.exit(1)


def update_serverless_function(name, project):
    local_function = LocalServerlessFunction(project, name)
    local_function.validate_for_update()
    local_function.upload_code()
    result = shell.run('yc', 'serverless', 'function', 'version', 'create',  *local_function.generate_yc_update_arguments())
    util.assert_with_actions(not result.return_code, f'ERROR: failed yc command\n{result.stderr}')
    print('success')


def create_serverless_function(name, project):
    local_function = LocalServerlessFunction(project, name)
    local_function.validate_for_creation()
    result = shell.run('yc', 'serverless', 'function', 'create',  *local_function.generate_yc_create_arguments())
    util.assert_with_actions(not result.return_code, f'ERROR: failed yc command\n{result.stderr}')
    print('success')


def main(args):
    if args.global_command == 'delete':
        delete_serverless_function(args.name)
    if args.global_command == 'create':
        create_serverless_function(args.name, args.project)
    if args.global_command == 'update':
        update_serverless_function(args.name, args.project)
    if args.global_command == 'list':
        print(get_list_of_serverless_functions())



parser = argparse.ArgumentParser(description='serverless utils')

cmd_subparser = parser.add_subparsers(help='Subcommands', dest='global_command', required=True)

delete_function = cmd_subparser.add_parser('delete')
delete_function.add_argument('name')

list_function = cmd_subparser.add_parser('list')


create_function = cmd_subparser.add_parser('create')
create_function.add_argument('project')
create_function.add_argument('name')

update_function = cmd_subparser.add_parser('update')
update_function.add_argument('project')
update_function.add_argument('name')



if __name__ == "__main__":
    main(parser.parse_args())
