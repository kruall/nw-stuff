import json
import sys


def to_lines(post):
    lines = [post['name']]
    for k, v in post.get('properties', {}).items():
        lines.append(f'{k}: {v}')
    for idx, block in enumerate(post.get('content', [])):
        if not block:
            continue
        if idx:
            lines += ['', '', block[0]]
            text = block[1:]
        else:
            text = block
        lines.append('')
        lines += text
    return lines


def main():
    path_to_json = sys.argv[1]
    path_to_file = sys.argv[2]

    content = []
    with open(path_to_json, 'r') as file:
        content = json.load(file)

    with open(path_to_file, 'w') as file:
        for post in sorted(content, key=lambda x: x['name']):
            print(post['name'])
            print('\n'.join(to_lines(post)), file=file)
            print(file=file)
            print(file=file)


if __name__ == '__main__':
    main()
