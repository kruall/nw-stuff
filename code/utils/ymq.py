import boto3
import json
import logging


logger = logging.getLogger()


client = boto3.client(
    service_name='sqs',
    endpoint_url='https://message-queue.api.cloud.yandex.net',
    region_name='ru-central1'
)


queue_url = 'fifo-msg-queue'

def send_generation_request(request):
    client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(request),
        MessageGroupId="small-gpu"
    )


def receive_generation_request():
    messages = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=60,
        WaitTimeSeconds=1,
        ReceiveRequestAttemptId="small-gpu"
    ).get('Messages')
    if messages:
        msg = messages[0]
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg.get('ReceiptHandle')
        )
        try:
            return json.loads(msg.get('Body'))
        except Exception as ex:
            logger.error(f'Error during receiving request {ex}')
    return None