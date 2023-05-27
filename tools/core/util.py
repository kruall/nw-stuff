import inspect
import os
import sys
import traceback

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


current_script_path = inspect.getframeinfo(inspect.currentframe()).filename
core_path = os.path.dirname(os.path.abspath(current_script_path))
tools_path = os.path.dirname(core_path)

assert os.path.basename(core_path) == 'core', "expected this script are in core"
assert os.path.basename(tools_path) == 'tools', "expected this script are in tools"

global_path = os.path.dirname(tools_path)

projects_path = os.path.join(global_path, 'projects')
scripts_path = os.path.join(global_path, 'scripts')
resources_path = os.path.join(global_path, 'resources')
out_path = os.path.join(global_path, 'out')
out_projects_path = os.path.join(out_path, 'projects')
configs_path = os.path.join(global_path, 'configs')
profiles_path = os.path.join(configs_path, 'profiles.yaml')


assert os.path.isdir(projects_path), f"expected projects directory '{projects_path}"
assert os.path.isdir(scripts_path), f"expected scripts directory '{scripts_path}"


class HaltError(Exception):
    def __init__(self, message, extra_message=None):
        if message is None:
            message = extra_message
            extra_message = None
        self._message = message
        self._extra_message = extra_message

    def __str__(self):
        if self._extra_message:
            return f'ERROR: {self._message}\n{self._extra_message}'
        if self._message:
            return 'ERROR: ' + self._message
        return 'HaltError'


def assert_with_actions(expr, msg, action=None, extra_msg=None):
    if not expr:
        if action is not None:
            action()
        if not msg and extra_msg:
            msg = extra_msg
            extra_msg = None
        raise HaltError(msg, extra_msg)


def validate_dir_existence(path, extra_msg=None):
    assert_with_actions(os.path.isdir(path), f"Expected directory '{path}'.", extra_msg=extra_msg)


def validate_file_existence(path, extra_msg=None):
    assert_with_actions(os.path.isfile(path), f"Expected file '{path}'.", extra_msg=extra_msg)


def validate_path_unexistence(path, extra_msg=None):
    assert_with_actions(not os.path.exists(path), f"Unexpected existence '{path}'.", extra_msg=extra_msg)


def catch_halt_error(main):
    def wrapped(*args, **kwargs):
        try:
            main(*args, **kwargs)
        except HaltError as Ex:
            print(Ex, file=sys.stderr)
            sys.exit(1)
    return wrapped


def load_profiles():
    assert_with_actions(os.path.isfile(profiles_path), f" Expected file '{profiles_path}'")
    with open(profiles_path, 'r') as file:
        yaml_file = yaml.load(file, Loader)
    return {x['name'] : x for x in yaml_file['profiles']}


def get_profile(name):
    profiles = load_profiles()
    assert_with_actions(name in profiles, f"Expected profile {name} in file '{profiles_path}'")
    return profiles[name]
