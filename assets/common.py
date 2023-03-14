import boto3
import sys
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

def temp_session(sts_response, region):
    session = boto3.Session(
        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
        aws_session_token=sts_response['Credentials']['SessionToken'],
        region_name=region
    )
    return session


def sqs_client(session):
    sqs = session.client('sqs')
    return sqs


def get_sqs_msgs(sqs_client, sqs_queue_name, attributes=[], group_id="", max_messages=10, visibility_time=10, wait_time=10):
    sqs_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    response = sqs_client.receive_message(
        QueueUrl=sqs_url["QueueUrl"],
        AttributeNames=["MessageGroupId"],
        MaxNumberOfMessages=max_messages,
        MessageAttributeNames=attributes,
        VisibilityTimeout=visibility_time,
        WaitTimeSeconds=wait_time
    )

    msgs = []
    if response.get("Messages") is not None:
        for msg in response.get("Messages"):
            # Catch exception where message has empty 'MessageAttributes'
            try:
                if msg["Attributes"]["MessageGroupId"] == group_id and check_attributes(attributes, msg.get("MessageAttributes").keys()):
                    msgs.append(msg)
            except AttributeError:
                return msgs

    return msgs

def delete_sqs_msg(sqs_client, sqs_queue_name, receipt_handle):
    sqs_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    response = sqs_client.delete_message(
        QueueUrl=sqs_url["QueueUrl"],
        ReceiptHandle=receipt_handle
    )
