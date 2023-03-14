# AWS SQS Message Resource

## Source configuration
* `sqs_queue`: *Required.* The name of the SQS Queue.

* `access_key_id`: *Required.* The AWS access key to use when accessing the
  bucket.

* `secret_access_key`: *Required.* The AWS secret key to use when accessing
  the bucket.

* `aws_role_arn`: *Required.* The AWS role ARN to be assumed by the user
  identified by `access_key_id` and `secret_access_key`.

* `region_name`: *Required.* The region the bucket is in. Defaults to
  `us-east-1`.

* `msg_attributes`: *Required.* The SQS Message attributes used to filter messages from the SQS Queue.

## Behaviour
### `check`: Check for new messages on SQS Queue
Detects new messages posted to the SQS Queue.
### `in`: Retrieve messages to SQS Queue
Retrieves new messages posted to the SQS Queue.
### `out`: Post messages to SQS Queue
Post messages to the SQS Queue.

**To be developed**

## Development testing (Command Line)
### `check`
#### Test Input
`check.json`...
```
{
  "source": {
    "sqs_queue_name": "<AWS SQS Queue Name>",
    "access_key_id": "<AWS Account Access Key>",
    "secret_access_key": "<AWS Account Secret Key>",
    "role_arn": "arn:aws:iam::1234567890:role/concourse-sqs-role",
    "region": "eu-west-2",
    "msg_attributes": ["Attribute_01","Attribute_02"]
  }
}
```
#### Execution
```
cat /tmp/check.json | /usr/local/bin/python3.9 /Users/watshamm/PycharmProjects/sqs-resource/assets/check.py
```
### `in`
#### Test input
`in.json`...
```
{
  "source": {
    "sqs_queue_name": "<AWS SQS Queue Name>",
    "access_key_id": "<AWS Account Access Key>",
    "secret_access_key": "<AWS Account Secret Key>",
    "role_arn": "arn:aws:iam::1234567890:role/concourse-sqs-role",
    "region": "eu-west-2",
    "msg_attributes": ["Attribute_01","Attribute_02"],
    "dest_file": "messages.json"
  },
  "version": {"msg_id": "None"}
}
```
#### Execution
```
cat /tmp/in.json | /usr/local/bin/python3.9 /Users/watshamm/PycharmProjects/sqs-resource/assets/in.py ../
```
## Development Testing (local container)
### Build container
`docker build . -t mwatsham/sqs-resource`
### `check`
`check.json`...
```
{
  "source": {
    "sqs_queue_name": "<AWS SQS Queue Name>",
    "access_key_id": "<AWS Account Access Key>",
    "secret_access_key": "<AWS Account Secret Key>",
    "role_arn": "arn:aws:iam::1234567890:role/concourse-sqs-role",
    "region": "eu-west-2",
    "msg_attributes": ["Attribute_01","Attribute_02"]
  }
}
```
#### Test input
#### Execution
`docker run --rm -i -v "${PWD}:${PWD}" -w "${PWD}" mwatsham/sqs-resource /opt/resource/check . < check.json`
### `in`
#### Test input
`in.json`...
```
{
  "source": {
    "sqs_queue_name": "<AWS SQS Queue Name>",
    "access_key_id": "<AWS Account Access Key>",
    "secret_access_key": "<AWS Account Secret Key>",
    "role_arn": "arn:aws:iam::1234567890:role/concourse-sqs-role",
    "region": "eu-west-2",
    "msg_attributes": ["Attribute_01","Attribute_02"],
    "dest_file": "messages.json"
  },
  "version": {"msg_id": "None"}
}
```
#### Execution
`docker run --rm -i -v "${PWD}:${PWD}" -w "${PWD}" mwatsham/sqs-resource /opt/resource/in . < in.json`

## Upload to Docker Hub
Note the following architecture specification especially when building on an M1 Mac
`docker buildx build --platform linux/amd64 -t mwatsham/sqs-resource --push .`

# Credits/References
* https://concourse-ci.org/implementing-resource-types.html
* https://medium.com/devops-dudes/writing-a-custom-concourse-resource-overview-1ed6d2983e39