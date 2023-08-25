# AWS SQS Message Resource

## Concept
In the context of AWS SQS message queues the Concourse CI Resource Type check , in , and out  scripts will be used as follows...

### `check` 
  * Will poll a specified AWS SQS queue for new messages.
  * Treats the discovery of new messages as a 'new version'.
  * Outputs an array of SQS Message IDs for new messages up to a default maximum of 10 messages (AWS SQS Message Quotas) per check invocation. 
### `in` 
  * Uses the destination directory passed in as command line argument $1 as the destination for JSON file that will contain the consumed AWS SQS messages.
  * Consumes and removes up to a default maximum of 10 messages (AWS SQS Message Quotas) per in  invocation for the a specified AWS SQS queue. 
  * Writes a file in the destination directory supplied argument $1  that contains a JSON array of the messages consumed from the AWS SQS queue. The intention is that this directory and file can be made available to the Concourse CI pipeline. The message JSON file contents can then be consumed as desired in the pipeline jobs/tasks.
### `out` 
  * Offers the ability to post messages to a specified AWS SQS queue.
  * The intention is to invoke the out script to capture Concourse CI on_success and on_failure events.
  * Offers the capability to output message attributes and message body content via Concourse CI put 'params'.
  * Offers the capability to include Concourse CI task output file content as part of the message body.
  * Message body can formatted in either text, JSON, or XML.


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

* `msg_attributes`: *Optional.* The SQS Message attributes used to filter messages from the SQS Queue.

* `msg_group_id`: *Required for SQS FIFO queues.* The SQS group id tag that specifies that a message belongs 
  to a specific message group. Messages that belong to the same message group are always processed one by one, 
  in a strict order relative to the message group.

* `dest_file`: *Optional.* Default: `messages.json`, File to capture JSON formatted output of messages attributes and
  message body.

## Behaviour
### `check`: Check for new messages on SQS Queue
Detects new messages posted to the SQS Queue.
### `in`: Retrieve messages to SQS Queue
Retrieves new messages posted to the SQS Queue.
### `out`: Post messages to SQS Queue
Post messages to the SQS Queue.


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
