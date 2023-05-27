import inspect
import os
import sys

current_script_path = inspect.getframeinfo(inspect.currentframe()).filename
filesharing_path = os.path.dirname(os.path.abspath(current_script_path))
tools_path = os.path.dirname(filesharing_path)
sys.path.insert(1, tools_path)


assert os.path.basename(filesharing_path) == 'filesharing', "expected this script are in file-sharing"
assert os.path.basename(tools_path) == 'tools', "expected this script are in tools"


import argparse

import core.util as util
import filesharing.logic as logic



@util.catch_halt_error
def main(args):
    if args.global_command == 'list':
        for name in logic.list_of_files():
            print(name)
    if args.global_command == 'upload':
        if not args.name:
            args.name = os.path.basename(args.path)
        logic.upload_file(args.path, args.name)
    if args.global_command == 'download':
        if not args.path:
            args.path = args.name
        logic.download_file(args.name, args.path)


parser = argparse.ArgumentParser(description='file sharing utils')

cmd_subparser = parser.add_subparsers(help='Subcommands', dest='global_command', required=True)

list_function = cmd_subparser.add_parser('list')

upload_function = cmd_subparser.add_parser('upload')
upload_function.add_argument('path')
upload_function.add_argument('--name')

download_function = cmd_subparser.add_parser('download')
download_function.add_argument('name')
download_function.add_argument('--path')


if __name__ == "__main__":
    main(parser.parse_args())
