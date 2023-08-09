#!/usr/bin/env python

import json
import os
import sys

from common import *


def _post_sqs_msg():


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

    content = _post_sqs_msgs(sqs_response, sqs_queue_name, msg_attributes, msg_group_id)

if __name__ == '__main__':
    _main(sys.stdin, sys.argv[1])