#!/usr/bin/env python

import json
import sys

from common import *


def _check_sqs_msg(sqs_client, sqs_queue_name, attributes):
    msgs = get_sqs_msgs(sqs_client, sqs_queue_name, attributes)

    msg_id = []

    # Check if SQS messages exist
    if msgs:
        for msg in msgs:
            msg_id.append({"msg_id": msg.get("MessageId")})

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

    temp_session_response = temp_session(sts_response, region)

    sqs = sqs_client(temp_session_response)

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
