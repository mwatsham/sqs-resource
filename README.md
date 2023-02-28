# AWS SQS Message Resource

## Source configuration
* `sqs_queue`: *Required.* The name of the SQS Queue.

* `access_key_id`: *Optional.* The AWS access key to use when accessing the
  bucket.

* `secret_access_key`: *Optional.* The AWS secret key to use when accessing
  the bucket.

* `session_token`: *Optional.* The AWS STS session token to use when
  accessing the bucket.

* `aws_role_arn`: *Optional.* The AWS role ARN to be assumed by the user
  identified by `access_key_id` and `secret_access_key`.

* `region_name`: *Optional.* The region the bucket is in. Defaults to
  `us-east-1`.

## Behaviour
### `check`: Check for new messages on SQS Queue
Detects new messages posted to the SQS Queue.
### `in`: Retrieve messages to SQS Queue
Retrieves new messages posted to the SQS Queue.
### `out`: Post messages to SQS Queue
Post messages to the SQS Queue.

# Credits/References
* https://concourse-ci.org/implementing-resource-types.html
* https://medium.com/devops-dudes/writing-a-custom-concourse-resource-overview-1ed6d2983e39