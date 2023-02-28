#!/usr/bin/env python

import json
import os
import sys

from common import *


def _receive_sqs_msg(sqs, sqs_queue_name, attributes):
    sqs_queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    messages = sqs_queue.receive_messages(
        MaxNumberOfMessages=10,
        MessageAttributeNames=attributes,
        VisibilityTimeout=10,
        WaitTimeSeconds=0
    )
    received_messages = []
    for msg in messages:
        attribute_value = ""
        msg_attributes = {}
        for attribute in attributes:
            if msg.message_attributes.get(attribute) is not None:
                attribute_value = msg.message_attributes.get(attribute).get('StringValue')
                msg_attributes[attribute] = attribute_value
        received_messages.append(msg_attributes)
        msg.delete()
    return received_messages


def _in(content, dest_dir, dest_file):
    filename = os.path.join(dest_dir, dest_file)
    with open('{}'.format(filename), 'w') as f:
        json.dump(content, f)


def _main(in_stream, dest_dir='.'):
    payload = json.load(in_stream)
    resource_source = payload['source']
    version = payload['version']['key']

    role_arn = resource_source['role_arn']
    access_key_id = resource_source['access_key_id']
    secret_access_key = resource_source['secret_access_key']
    region = resource_source['region']
    sqs_queue_name = resource_source['sqs_queue_name']
    msg_attributes = resource_source['msg_attributes']
    dest_file = resource_source['dest_file']

    sts_response = sts_session(role_arn, access_key_id, secret_access_key)

    temp_session_response = new_session(sts_response, region)

    sqs = sqs_resource(temp_session_response)

    content = _receive_sqs_msg(sqs, sqs_queue_name, msg_attributes)

    _in(content, dest_dir, dest_file)

    print(json.dumps({"version": {"key": version}, "metadata": content}))


if __name__ == '__main__':
    _main(sys.stdin,sys.argv[1])
    #dest_dir = '.'
    #source = {
    #    'source': {
    #        'sqs_queue_name': os.environ.get('AWS_SQS_QUEUE_NAME'),
    #        'access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
    #        'secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
    #        'role_arn': os.environ.get('AWS_ROLE_ARN'),
    #        'msg_attributes': ['Hostname'],
    #        'dest_file': 'vm_hosts.json'
    #    },
    #    "version": {"key": None}
    #}

    # _main(json.dumps(source), dest_dir)
