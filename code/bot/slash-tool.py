import requests
import sys

from lib.common import variables


discord_url = f'https://discord.com/api/v8/applications/{variables.discord_application_id}/commands'

if not variables.discord_application_id or not variables.bot_key:
    print('not credentials')
    sys.exit(1)

def make_headers():
    return {
        'Authorization': f'Bot {variables.bot_key}',
        'Content-Type': 'application/json'
    }



class Command:
    def __init__(self, **command_args):
        self.json = command_args
    
    def add_option(self, **option_args):
        if 'options' not in self.json:
            option_list = []
            self.json['options'] = option_list
        else:
            option_list = self.json['options']

        option_list.append(option_args)
        return self

    def add_text_option(self, **option_args):
        return self.add_option(type=3, **option_args)

    def add_required_text_option(self, **option_args):
        return self.add_text_option(required=True, **option_args)


bot_commands = [
    Command(name='args', description='show current agrs'),
    (Command(name='set', description='set arg value')
        .add_required_text_option(name='arg', description='arg name')
        .add_required_text_option(name='arg_value', description='value')),
    (Command(name='del', description='delete arg')
        .add_required_text_option(name='arg', description='arg name')),
    (Command(name='gen', description='generate text')
        .add_required_text_option(name='prompt', description='input text')),
    (Command(name='model', description='change model')
        .add_required_text_option(name='model', description='model name in huggish face')),
]


def get_commands():
    response = requests.get(discord_url, headers=make_headers())
    return response.json()


def create_command(cmd_json):
    requests.post(discord_url, json=cmd_json, headers=make_headers())


def delete_command(cmd_id):
    delete_url = f'{discord_url}/{cmd_id}'
    requests.delete(delete_url, headers=make_headers())


def check_command(expected, real):
    if ('options' in expected) != ('options' in real):
        print(f"not_ok_options; expected: {'options' in expected} real: {'options' in real}")
        return False

    for k, v in expected.items():
        if k == 'options':
            real_options = real['options']
            if len(v) != len(real_options):
                print(f"not_ok_options; expected: size {len(v)} real: size {len(real_options)}")
                return False
            for idx, opt_d in enumerate(v):
                for opt_k, opt_v in opt_d.items():
                    if real_options[idx].get(opt_k, None) != opt_v:
                        print(f"not_ok_option_kv; expected: ({opt_k}, {opt_v}) real: ({opt_k}, {real_options[idx].get(opt_k, None)})")
                        return False
        elif real.get(k, None) != v:
            print(f"not_ok_cmd_kv; expected: ({k}, {v}) real: ({k}, {real.get(k, None)})")
            return False

    return True


def sync_commands(create_new=False, overwrite_not_same=False, delete_unexpected=False):
    real_commands = get_commands()
    real_command_dict = {cmd['name']: cmd for cmd in real_commands}

    missed_commands = []
    expected_commands = {bot_cmd.json['name'] for bot_cmd in bot_commands}
    unexpected_commands = {cmd_name: cmd_json['id'] for cmd_name, cmd_json in real_command_dict.items() if cmd_name not in expected_commands}

    for bot_cmd in bot_commands:
        command_name = bot_cmd.json['name']
        if command_name not in real_command_dict:
            print(f'command "{command_name}" WAS NOT CREATED')
            if create_new:
                missed_commands.append(bot_cmd.json)
        elif not check_command(bot_cmd.json, real_command_dict[command_name]):
            print(f'command "{command_name}" WAS NOT SAME')
            print('expected:', bot_cmd.json)
            print('current:', real_command_dict[command_name])
            if overwrite_not_same:
                missed_commands.append(bot_cmd.json)
        else:
            print(f'comman "{command_name}" OK')

    for command_name, command_id in unexpected_commands.items():
        print(f'command "{command_name}" UNEXPECTED')
        if delete_unexpected:
            delete_command(command_id)
            print(f'command "{command_name}" REMOVED')

    for ms_cmd in missed_commands:
        create_command(ms_cmd)
        command_name = ms_cmd['name']
        print(f'command "{command_name}" CREATED')


sync_commands(create_new=True, overwrite_not_same=True, delete_unexpected=True)
