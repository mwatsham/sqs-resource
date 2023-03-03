#!/usr/bin/env python

import json
import sys

from common import *


def _check_sqs_msg(sqs, sqs_queue_name, attributes):
    sqs_queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    messages = sqs_queue.receive_messages(
        MaxNumberOfMessages=10,
        MessageAttributeNames=attributes,
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    msg_id = []
    for msg in messages:
        if msg.message_attributes is not None:
            msg_id.append({"msg_id": str(msg.message_id)})
    return msg_id


def _main(in_stream):
    payload = json.load(in_stream)
    resource_source = payload['source']

    role_arn = resource_source['role_arn']
    access_key_id = resource_source['access_key_id']
    secret_access_key = resource_source['secret_access_key']
    region = resource_source['region']
    sqs_queue_name = resource_source['sqs_queue_name']
    msg_attributes = resource_source['msg_attributes']

    sts_response = sts_session(role_arn, access_key_id, secret_access_key)

    temp_session_response = new_session(sts_response, region)

    sqs = sqs_resource(temp_session_response)

    print(json.dumps(_check_sqs_msg(sqs, sqs_queue_name, msg_attributes)))


if __name__ == '__main__':
    _main(sys.stdin)
    #source = {
    #    "source": {
    #        "sqs_queue_name": os.environ.get('AWS_SQS_QUEUE_NAME'),
    #        "access_key_id": os.environ.get('AWS_ACCESS_KEY_ID'),
    #        "secret_access_key": os.environ.get('AWS_SECRET_ACCESS_KEY'),
    #        "role_arn": os.environ.get('AWS_ROLE_ARN')
    #    },
    #    "version": None
    #}

    #_main(json.dumps(source))
