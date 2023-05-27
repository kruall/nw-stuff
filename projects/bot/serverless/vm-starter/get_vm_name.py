import json

line = input()

request = json.loads(line)

print(request.get('body', "UNKNOWN"))