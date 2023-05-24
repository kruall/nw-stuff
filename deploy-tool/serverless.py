import subprocess
import json
import sys
import argparse
import inspect
import os


class ProcResult:
    def __init__(self, completed_process):
        self.return_code = completed_process.returncode
        self.stdout = completed_process.stdout.encode('utf-8') if completed_process.stdout else ''
        self.stderr = completed_process.stderr.encode('utf-8') if completed_process.stderr else ''


def shell(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_list_of_serverless_functions():
    cmd = 'yc serverless function list --format=json'
    proc = shell(cmd)
    if proc.returncode != 0:
        print(f"ERROR: command failed '{cmd}'", file=sys.stderr)
        print(f"{proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout)


def delete_serverless_function(name):
    cmd = f"yc serverless function delete --name='{name}'"
    proc = shell(cmd)
    if proc.returncode == 0:
        print('success')
    else:
        print(f"ERROR: command failed '{cmd}'", file=sys.stderr)
        print(f"{proc.stderr}", file=sys.stderr)
        sys.exit(1)


def validate_dir_existence(path):
    if not os.path.isdir(path):
        print(f"ERROR: Expected directory '{path}", file=sys.stderr)
        sys.exit(1)


def validate_path_unexistence(path):
    if os.path.exists(path):
        print(f"ERROR: Unexpected directory '{path}", file=sys.stderr)
        sys.exit(1)



def create_serverless_function(name, proj):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.dirname(os.path.abspath(filename)))
   
    code_path = os.path.join(path, 'code')
    validate_dir_existence(code_path)
    function_path = os.path.join(code_path, proj, 'serverless', name)
    validate_dir_existence(function_path)
    config_path = os.path.join(function_path, '.config')
    validate_dir_existence(config_path)

    out_path = os.path.join(path, 'out')
    validate_path_unexistence(out_path)

    print(path, out_path, function_path)


def main(args):
    if args.global_command == 'delete':
        delete_serverless_function(args.name)
    if args.global_command == 'create':
        create_serverless_function(args.name, args.project)
    else:
        print(get_list_of_serverless_functions())



parser = argparse.ArgumentParser(description='serverless utils')

cmd_subparser = parser.add_subparsers(help='Subcommands', dest='global_command', required=True)

delete_function = cmd_subparser.add_parser('delete')
delete_function.add_argument('name')

list_function = cmd_subparser.add_parser('list')


create_function = cmd_subparser.add_parser('create')
create_function.add_argument('project')
create_function.add_argument('name')



if __name__ == "__main__":
    main(parser.parse_args())
