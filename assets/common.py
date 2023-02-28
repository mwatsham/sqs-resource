import boto3


def sts_session(role_arn, access_key, secret_key):
    aws_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    sts = aws_session.client('sts')
    response = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="sts-session"
    )
    return response


def new_session(sts_response, region):
    session = boto3.Session(
        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
        aws_session_token=sts_response['Credentials']['SessionToken'],
        region_name=region
    )
    return session


def sqs_resource(session_response):
    sqs = session_response.resource('sqs')
    return sqs
