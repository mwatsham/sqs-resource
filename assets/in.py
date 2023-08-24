#!/usr/bin/env python

import json
import os
import sys

from common import *


# Function: _process_sqs_msg
# Parameters:
#   - sqs_client: boto3 low-level SQS Client object
#   - sqs_queue_name:
#   - attributes:
# Description: Function to process messages from SQS Message Queue
def _process_sqs_msgs(sqs_client, sqs_queue_name, attributes, group_id, implicit_get=False):
    # 'implicit_get' used to determine if funtion call is part of the implicit get step
    # invoked by a put step. If the call is part of a put step then we don't want SQS messages
    # hidden or deleted from the SQS queue.
    # Safeguard if 'no_get' is not specified in the put step.
    if implicit_get:
        msgs = get_sqs_msgs(sqs_client, sqs_queue_name, attributes, group_id, visibility_time=0, wait_time=0)
    else:
        msgs = get_sqs_msgs(sqs_client, sqs_queue_name, attributes, group_id)

    received_messages = []

    if msgs:
        for msg in msgs:
            msg_attributes = {}

            for attribute in msg.get("MessageAttributes").keys():
                attribute_value = msg["MessageAttributes"][attribute]["StringValue"]
                msg_attributes[attribute] = attribute_value

            msg_attributes['msg_id'] = msg.get("MessageId")

            # If message body is valid JSON, format it as JSON, else dump out as is.
            try:
                msg_attributes['msg_body'] = json.loads(msg.get("Body"))
            except ValueError:
                msg_attributes['msg_body'] = msg.get("Body")

            received_messages.append(msg_attributes)

            if not implicit_get:
                delete_sqs_msg(sqs_client, sqs_queue_name, msg.get("ReceiptHandle"))
    return received_messages


def _in(content, dest_dir, dest_file):
    filename = os.path.join(dest_dir, dest_file)
    with open('{}'.format(filename), 'w') as f:
        json.dump(content, f)


def _main(in_stream, dest_dir='.'):
    print(in_stream, file=sys.stderr)
    payload = process_payload(json.loads(in_stream))

    # Get STS credentials for assume role
    sts_response = sts_session(payload['role_arn'], payload['access_key_id'], payload['secret_access_key'])

    # Get new client session using temporary STS credentials
    temp_session_response = temp_session(sts_response, payload['region'])

    # Return SQS Client
    aws_client = sqs_client(temp_session_response)

    content = _process_sqs_msgs(aws_client, payload['sqs_queue_name'], payload['msg_attributes'], payload['msg_group_id'])

    _in(content, dest_dir, payload['dest_file'])

    print(json.dumps({"version": payload['version'], "metadata": content}))


if __name__ == '__main__':
    source = sys.stdin.read()
    _main(source, sys.argv[1])
