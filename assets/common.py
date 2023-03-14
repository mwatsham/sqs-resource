import boto3


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


def get_sqs_msgs(sqs_client, sqs_queue_name, attributes):
    sqs_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    response = sqs_client.receive_message(
        QueueUrl=sqs_url["QueueUrl"],
        MaxNumberOfMessages=10,
        MessageAttributeNames=attributes,
        VisibilityTimeout=2,
        WaitTimeSeconds=0
    )

    msgs = []

    if response.get("Messages") is not None:
        for msg in response.get("Messages"):
            msgs.append(msg)

    return msgs

def delete_sqs_msg(sqs_client, sqs_queue_name, receipt_handle):
    sqs_url = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    response = sqs_client.delete_message(
        QueueUrl=sqs_url["QueueUrl"],
        ReceiptHandle=receipt_handle
    )
