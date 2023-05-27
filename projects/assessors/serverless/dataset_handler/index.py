import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def make_response(text: str):
    return {
        'statusCode': 200,
        'headers': {"Content-Type": "application/json"},
        'body': json.dumps({ })
    }


def handler(event, context):
    return make_response('waiting server response')
