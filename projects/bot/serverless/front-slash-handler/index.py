import json
import logging

import requests

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from lib.common import variables
from lib.request import start_vm, get_internal_headers
from lib.ymq import send_generation_request


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def verify_signature(body, signature, timestamp):
    message = timestamp.encode() + body.encode()
    verify_key = VerifyKey(bytes.fromhex(variables.public_key))
    verify_key.verify(message, bytes.fromhex(signature)) # raises an error if unequal



def request_generate(command_body):
    url = '<some-url>'

    request_body = {
        'command': command_body['data']['name'],
        'token':  command_body['token'],
        'application_id': command_body['application_id'],
        'options': [opt['value'] for opt in command_body['data'].get('options', [])]
    } 

    send_generation_request(request_body)
    vm_name = 'small-gpu'
    start_vm(vm_name)
    logger.debug(str(request_body))
    # requests.post(url, json=request_body, headers=get_internal_headers(), timeout=1.0)


def make_response(text: str):
    return {
        'statusCode': 200,
        'headers': {"Content-Type": "application/json"},
        'body': json.dumps({
            'type': 4,
            'data': {
                'tts': False,
                'content': text,
                'allowed_mentions': []
            }
        })
    }


def handler(event, context):
    try:
        signature = event['headers']["X-Signature-Ed25519"]
        timestamp = event['headers']["X-Signature-Timestamp"]
        verify_signature(event['body'], signature, timestamp)
    except Exception as e:
        logger.error(f"Response 401; {e}")
        return {
			'statusCode': 401,
		}

    try:
        body = json.loads(event['body'])
        request_generate(body)
        return make_response('waiting server response')
    except Exception as e:
        logger.error(f"Response error with 200; {e}")
        return make_response(f'something go wrong: {e}')