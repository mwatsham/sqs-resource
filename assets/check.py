#!/usr/bin/env python

import json
import sys

from common import *


def _check_sqs_msg(client, sqs_queue_name, attributes, group_id=""):
    # Note that the message attributes visibility and waitfortime are set to 0
    # as this is only checking to see if new messages exist. There is no need to
    # hide message.
    msgs = get_sqs_msgs(client, sqs_queue_name, attributes, group_id, visibility_time=0, wait_time=0)

    msg_id = []

    # Check if SQS messages exist
    if msgs:
        for msg in msgs:
            msg_id.append({"msg_id": str(msg.get("MessageId"))})

    return msg_id


def _main(in_stream):
    print(in_stream, file=sys.stderr)

    payload = process_payload(json.loads(in_stream))

    # Get STS credentials for assume role
    sts_response = sts_session(payload['role_arn'], payload['access_key_id'], payload['secret_access_key'])

    # Get new client session using temporary STS credentials
    temp_session_response = temp_session(sts_response, payload['region'])

    # Return SQS Client
    aws_client = sqs_client(temp_session_response)

    versions = _check_sqs_msg(
        aws_client,
        payload['sqs_queue_name'],
        payload['msg_attributes'],
        payload['msg_group_id']
    )

    print(json.dumps(versions))


if __name__ == '__main__':
    source = sys.stdin.read()
    _main(source)
