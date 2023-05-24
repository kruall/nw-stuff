import bs4
import requests


class InteractiveParser:
    def __init__(self):
        self._link = None
        self._current_nodes = None

    def _check_unexpected_args(self, *args, **kwargs):
        if args:
            print('Unexpected args')
        if kwargs:
            print('Unexpected kwargs')

    def _cmd_exit(self, *args, **kwargs):
        return False
    
    _cmd_q = _cmd_exit

    def _cmd_reset(self, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)
        self._current_nodes = None
        return True
    
    def _cmd_parent(self, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)

        parents = set()
        for node in self._current_nodes:
            if node.parent:
                parents.add(node.parent)
        self._current_nodes = list(parents)
        return True
    
    def _cmd_children(self, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)

        children = list()
        for node in self._current_nodes:
            children += node.children

        self._current_nodes = children
        return True
    
    def _view_node(self, node, view=None):
        if view == 'pretty':
            return node.prettify() if not isinstance(node, bs4.NavigableString) else node
        elif view == 'tag':
            return node.name
        elif view == 'strings':
            return '\n' + '\n'.join(node.strings)
        elif view == 'stripped_strings':
            return '\n' + '\n'.join(node.stripped_strings)
        else:
            return node

    def _cmd_list(self, view=None, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)

        if self._current_nodes:
            for idx, node in enumerate(self._current_nodes):
                print(f'{idx}: {self._view_node(node, view)}')
        else:
            print("Don't have nodes")
        return True
    
    _cmd_ls = _cmd_list
    
    def _cmd_index(self, index, view=None, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)
        index = int(index)

        if self._current_nodes and index < len(self._current_nodes):
            print(f'{index}: {self._view_node(self._current_nodes[index], view)}')
        else:
            print("Don't have nodes")
        return True
    
    def _cmd_new_link(self, link, *args, **kwargs):
        self._check_unexpected_args(*args, **kwargs)
        self._link = link
        response = requests.get(self._link)
        self._soup = bs4.BeautifulSoup(response.text, 'html5lib')

    def _cmd_down(self, tag_name=None, **kwargs):
        if not self._current_nodes:
            next_nodes = self._soup.find_all(tag_name, **kwargs)
        else:
            next_nodes = []
            for node in self._current_nodes:
                if node and not isinstance(node, bs4.NavigableString):
                    next_nodes += node.find_all(tag_name, **kwargs)
        self._current_nodes = next_nodes
        return True

    def _parse_arguments(self, cmd):
        words = cmd.split()
        raw_args = words[1:]
        args = []
        kwargs = {}
        for arg in raw_args:
            if '=' in arg:
                key, word = arg.split('=', 1)
                kwargs[key] = word
            else:
                args.append(arg)
        return args, kwargs
    
    def _get_command_list(self):
        command_list = []
        for k, v in self.__class__.__dict__.items():
            if k.startswith('_cmd_'):
                command_list.append((k[5:], v))
        return command_list

    def _parse_command(self, cmd):
        for name, func in self._get_command_list():
            if not cmd.startswith(name):
                continue
            args, kwargs = self._parse_arguments(cmd)
            return lambda: func(self, *args, **kwargs)
        return None

    def _iteration(self):
        if self._link is None:
            self._link = input('Link: ')
            response = requests.get(self._link)
            self._soup = bs4.BeautifulSoup(response.text, 'html5lib')
        cmd = input(':')
        action = self._parse_command(cmd)
        if action:
            return action()
        else:
            print(f'Unknown command "{cmd}"')
            return True

    def run(self):
        while self._iteration():
            pass


if __name__ == '__main__':
    InteractiveParser().run()
