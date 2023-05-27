import json
import logging

import requests

from lib.common import variables
from lib.request import get_internal_headers
from lib.ydb import get_profile, list_profile_names, set_profile


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



def make_response(code: int, text: str):
    return {
        'statusCode': code,
        'headers': {"Content-Type": "application/json"},
        'body': text
    }


def handler(event, context):
    try:
        body = json.loads(event['body'])
        return make_response('')

    except Exception as e:
        logger.error(f"Response error with 500; {e}")
        return make_response(500, f'something go wrong: {e}')