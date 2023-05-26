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
deploy_tool_path = os.path.dirname(os.path.abspath(current_script_path))

global_path = os.path.dirname(deploy_tool_path)

code_path = os.path.join(global_path, 'code')
scripts_path = os.path.join(global_path, 'scripts')
resources_path = os.path.join(global_path, 'resources')
out_path = os.path.join(global_path, 'out')
out_code_path = os.path.join(out_path, 'code')
configs_path = os.path.join(global_path, 'configs')
profiles_path = os.path.join(configs_path, 'profiles.yaml')


assert os.path.basename(deploy_tool_path) == 'deploy-tool', "expected this script are in deploy-tool"
assert os.path.isdir(code_path), f"expected code directory '{code_path}"
assert os.path.isdir(scripts_path), f"expected scripts directory '{scripts_path}"

s3_code_package = 'code-package'


def assert_with_actions(expr, msg, action=None, extra_msg=None):
    if not expr:
        if action is not None:
            action()
        if not msg and extra_msg:
            msg = extra_msg
            extra_msg = None
        if msg:
            print(msg, file=sys.stderr)
        else:
            traceback.print_last()
        if extra_msg:
            print(extra_msg, file=sys.stderr)
        sys.exit(1)


def load_profiles():
    assert_with_actions(os.path.isfile(profiles_path), f"ERROR: Expected file '{profiles_path}")
    with open(profiles_path, 'r') as file:
        yaml_file = yaml.load(file, Loader)
    return {x['name'] : x for x in yaml_file['profiles']}
