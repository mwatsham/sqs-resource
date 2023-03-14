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
def _process_sqs_msgs(sqs_client, sqs_queue_name, attributes, group_id):
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

            delete_sqs_msg(sqs_client, sqs_queue_name, msg.get("ReceiptHandle"))
    return received_messages


def _in(content, dest_dir, dest_file):
    filename = os.path.join(dest_dir, dest_file)
    with open('{}'.format(filename), 'w') as f:
        json.dump(content, f)


def _main(in_stream, dest_dir='.'):
    payload = json.load(in_stream)
    resource_source = payload['source']
    version = payload['version']['msg_id']

    role_arn = resource_source['role_arn']
    access_key_id = resource_source['access_key_id']
    secret_access_key = resource_source['secret_access_key']
    region = resource_source['region']
    sqs_queue_name = resource_source['sqs_queue_name']
    msg_group_id = resource_source['msg_group_id']
    msg_attributes = resource_source['msg_attributes']
    dest_file = resource_source['dest_file']

    # Get STS credentials for assume role
    sts_response = sts_session(role_arn, access_key_id, secret_access_key)

    # Get new client session using temporary STS credentials
    temp_session_response = temp_session(sts_response, region)

    # Return SQS Client
    sqs_response = sqs_client(temp_session_response)

    content = _process_sqs_msgs(sqs_response, sqs_queue_name, msg_attributes, msg_group_id)

    _in(content, dest_dir, dest_file)

    print(json.dumps({"version": {"msg_id": version}, "metadata": content}))


if __name__ == '__main__':
    _main(sys.stdin, sys.argv[1])
