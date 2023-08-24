import boto3
import sys
import json
from pprint import pprint


# Function to output messages to stderr. Useful for
# troubleshooting in Concourse CI
def debug_msg(msg, *args, **kwargs):
    if isinstance(msg, (dict, list)):
        pprint(msg, stream=sys.stderr)  # a way of pretty printing dictionaries that needs to be imported
    else:
        print(msg.format(*args, **kwargs), file=sys.stderr)  # printing to standard-error so Concourse will ignore it


# Function to check that the defined source attributes
# are provided in the message attributes
def check_attributes(defined_attributes, msg_attributes):
    for attribute in defined_attributes:
        if attribute not in msg_attributes:
            return False
    return True


# Function to retrieve temporary AWS Session via an assumed role
# Returns temporary AWS session credentials
def sts_session(role_arn, access_key, secret_key):
    # Create AWS session
    aws_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    # Create low-level STS client
    sts = aws_session.client('sts')

    # Retrieve temporary session credentials for assumed role
    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="sts-session"
    )

    # Return temporary session credentials
    return response


# Function to establish an AWS session using temporary AWS session credentials
# Returns an AWS Session object
def temp_session(sts_response, region):
    session = boto3.Session(
        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
        aws_session_token=sts_response['Credentials']['SessionToken'],
        region_name=region
    )
    return session


# Function to establish an SQS client session
# Returns an SQS client session object
def sqs_client(session):
    sqs = session.client('sqs')
    return sqs


# Function to consume SQS messages from a given SQS queue
def get_sqs_msgs(aws_client, sqs_queue_name, attributes, group_id="", max_messages=10, visibility_time=10, wait_time=10):
    sqs_url = aws_client.get_queue_url(QueueName=sqs_queue_name)
    attrs = attributes if attributes is not None else []

    if sqs_queue_name.endswith(".fifo"):
        response = aws_client.receive_message(
            QueueUrl=sqs_url["QueueUrl"],
            AttributeNames=["MessageGroupId"],
            MaxNumberOfMessages=max_messages,
            MessageAttributeNames=attrs,
            VisibilityTimeout=visibility_time,
            WaitTimeSeconds=wait_time
        )
    else:
        response = aws_client.receive_message(
            QueueUrl=sqs_url["QueueUrl"],
            MaxNumberOfMessages=max_messages,
            MessageAttributeNames=attrs,
            VisibilityTimeout=visibility_time,
            WaitTimeSeconds=wait_time
        )

    msgs = []
    if response.get("Messages") is not None:
        for msg in response.get("Messages"):
            # Catch exception where message has empty 'MessageAttributes'
            try:
                if sqs_queue_name.endswith(".fifo"):
                    if msg["Attributes"]["MessageGroupId"] == group_id and check_attributes(attrs, msg.get("MessageAttributes").keys()):
                        msgs.append(msg)
                else:
                    if check_attributes(attrs, msg.get("MessageAttributes").keys()):
                        msgs.append(msg)
            except AttributeError:
                return msgs

    return msgs


# Function to delete a SQS message from a given queue.
def delete_sqs_msg(sqs_client, sqs_queue_name, receipt_handle):
    sqs_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    response = sqs_client.delete_message(
        QueueUrl=sqs_url["QueueUrl"],
        ReceiptHandle=receipt_handle
    )


def process_payload(payload):
    resource_source = {}
    response = {'params': payload.get('params', {})}

    try:
        resource_source = payload['source']
    except KeyError as e:
        print(f'Error: Resource `source` dict not defined ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['role_arn'] = resource_source['role_arn']
    except KeyError as e:
        print(f'Error: AWS `role_arn` not defined in `source` dict ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['access_key_id'] = resource_source['access_key_id']
    except KeyError as e:
        print(f'Error: AWS `access_key_id` not defined in `source` dict ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['secret_access_key'] = resource_source['secret_access_key']
    except KeyError as e:
        print(f'Error: AWS `secret_access_key` not defined in `source` dict ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['region'] = resource_source['region']
    except KeyError as e:
        print(f'Error: AWS `region` not defined in `source` ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['sqs_queue_name'] = resource_source['sqs_queue_name']
    except KeyError as e:
        print(f'Error: AWS `sqs_queue_name` not defined in `source` dict ({e})', file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero status code

    try:
        response['msg_content_type'] = resource_source['msg_content_type']
        if (
            response['msg_content_type'] != 'JSON' and
            response['msg_content_type'] != 'XML' and
            response['msg_content_type'] != 'TXT'
        ):
            print(f'Error: SQS Message Body `msg_content_type` must be either `JSON`, `XML`, or `TEXT`', file=sys.stderr)
            sys.exit(1)  # Exit with a non-zero status code
    except KeyError as e:
        print(f'Warning: SQS Message Body `msg_content_type` not defined in `source` dict ({e}). Defaulting to `JSON`', file=sys.stderr)
        response['msg_content_type'] = 'JSON'

    # Check for SQS queue type. If FIFO `msg_group_id` is required.
    if response['sqs_queue_name'].endswith(".fifo"):
        try:
            response['msg_group_id'] = resource_source['msg_group_id']
        except KeyError as e:
            print(f'Error: AWS `msg_group_id` not defined in `source` dict ({e})', file=sys.stderr)
            sys.exit(1)  # Exit with a non-zero status code
    else:
        response['msg_group_id'] = ""

    response['version'] = payload.get('version', "")
    response['msg_attributes'] = resource_source.get('msg_attributes', None)
    response['dest_file'] = resource_source.get('dest_file', 'messages.json')

    return response


def is_json(json_str):
    try:
        json.loads(json_str)
    except ValueError as e:
        return False
    return True
