#!/usr/bin/env python

import json
import xml.etree.ElementTree as ET
import os

import botocore.exceptions

from common import *


def _post_sqs_msg(aws_client, sqs_queue_name, group_id, msg_body, attributes):
    attrs = attributes if attributes is not None else {}

    try:
        if sqs_queue_name.endswith(".fifo"):
            response = aws_client.send_message(
                QueueUrl=sqs_queue_name,
                MessageBody=str(msg_body),
                MessageAttributes=attrs,
                MessageGroupId=group_id
            )
        else:
            response = aws_client.send_message(
                QueueUrl=sqs_queue_name,
                MessageBody=str(msg_body),
                MessageAttributes=attrs
            )
        return response
    except botocore.exceptions.ClientError as e:
        print(f'Error: {e})')
        sys.exit(1)  # Exit with a non-zero status code


# Checks submitted params for any of the Concourse CI Resource metadata environment
# variables and extracts the values from the local environment.
# - https://concourse-ci.org/implementing-resource-types.html#resource-metadata
def extract_concourse_metadata(params):
    new_params = {}

    for k, v in params.items():
        # Test for and process nested 'dict' objects
        if type(v) is dict:
            new_params[k] = extract_concourse_metadata(v)
        else:
            if v.startswith("$BUILD_") or v.startswith("$ATC_"):
                new_params[k] = os.environ.get(v.strip("$"))
            else:
                new_params[k] = v

    return new_params

def _main(in_stream, src_dir='.'):
    print(in_stream, file=sys.stderr)
    payload = process_payload(json.loads(in_stream))
    msg_body_content = None
    input_file_path = payload['params'].get('input_file_path', '')

    # Test if `input_file_path` has been specified, indicating that the user wishes
    # to include Concourse input file in SQS message body
    if input_file_path != "":
        try:
            filename = os.path.join(src_dir, input_file_path)
            with open('{}'.format(filename), 'r') as f:
                input_file_content = f.read()

                if payload['msg_content_type'] == "JSON":
                    msg_body_content = {}
                    try:
                        msg_body_content['input_file'] = json.dumps(input_file_content)
                    except json.decoder.JSONDecodeError:
                        msg_body_content['input_file'] = input_file_content
                        print(f'Warning: Malformed JSON in input file. Adding content as string value instead.')
                elif payload['msg_content_type'] == "XML":
                    print(f'Notice: XML Input file format yet to be implemented.')
                    sys.exit(1)  # Exit with a non-zero status code
                elif payload['msg_content_type'] == "TXT":
                    msg_body_content = input_file_content
        except FileNotFoundError:
            print(f'Error: Specified `input_file_path` {payload["input_file_path"]} does not exist')
            sys.exit(1)  # Exit with a non-zero status code
    else:
        if payload['msg_content_type'] == "JSON":
            msg_body_content = {}
        elif payload['msg_content_type'] == "XML":
            msg_body_content = ET.ElementTree()
        elif payload['msg_content_type'] == "TXT":
            msg_body_content = ""

    processed_params = extract_concourse_metadata(payload['params'])

    print(processed_params, file=sys.stderr)

    # Merge 'params' 'msg_body' JSON with `msg_body_content
    if 'msg_body' in processed_params and payload['msg_content_type'] == "JSON":
        try:
            msg_body_content = msg_body_content | processed_params['msg_body']
        except TypeError:
            print('Unable to merge JSON Input file content and params', file=sys.stderr)

    # Merge 'params' 'msg_body' XML with `msg_body_content
    if 'msg_body' in processed_params and payload['msg_content_type'] == "XML":
        print('Notice: Unable to merge XML Input file content and params. Yet to be implemented.', file=sys.stderr)

    # Merge 'params' 'msg_body' Text with `msg_body_content
    if 'msg_body' in processed_params and payload['msg_content_type'] == "TXT":
        msg_body_content = msg_body_content + json.dumps(processed_params['msg_body'])

    print(msg_body_content, file=sys.stderr)

    # Get STS credentials for assume role
    sts_response = sts_session(payload['role_arn'], payload['access_key_id'], payload['secret_access_key'])

    # Get new client session using temporary STS credentials
    temp_session_response = temp_session(sts_response, payload['region'])

    # Return SQS Client
    aws_client = sqs_client(temp_session_response)

    content = _post_sqs_msg(
        aws_client=aws_client,
        sqs_queue_name=payload['sqs_queue_name'],
        attributes=payload['msg_attributes'],
        group_id=payload['msg_group_id'],
        msg_body=msg_body_content
    )

    print(content, file=sys.stderr)

    print(json.dumps({"version": {"ref": "None"}}))


if __name__ == '__main__':
    source = sys.stdin.read()
    _main(source, sys.argv[1])