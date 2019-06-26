import json
import logging
from io import StringIO

from cazoo_logger import config, SnsContext, CloudwatchContext
from . import LambdaContext

event = {
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:eu-west-1:476912836688:sftp_drop_topic:596e3157-e1ae-41c2-b14a-fffe67ef5f76",
            "Sns": {
                "Type": "Notification",
                "MessageId": "66591d01-0241-5751-bb17-486e5a6dcf91",
                "TopicArn": "arn:aws:sns:eu-west-1:476912836688:sftp_drop_topic",
                "Subject": "Amazon S3 Notification",
                "Message": "...",
                "Timestamp": "2019-06-03T17:16:28.534Z",
                "SignatureVersion": "1",
                "Signature": "...",
                "SigningCertUrl": "",
                "UnsubscribeUrl": "",
                "MessageAttributes": {},
            },
        }
    ]
}


def test_basic_fields():

    stream = StringIO()
    config(stream)

    ctx = LambdaContext(
        request_id="abc123", function_name="do-things", function_version="0.1.2.3"
    )

    logger = SnsContext(event, ctx, logging.getLogger())
    logger.info("Hello world")

    result = json.loads(stream.getvalue())
    print(stream.getvalue())

    assert result == {
        "msg": "Hello world",
        "context": {
            "request_id": "abc123",
            "function": {"name": "do-things", "version": "0.1.2.3"},
            "sns": {
                "id": "66591d01-0241-5751-bb17-486e5a6dcf91",
                "topic": "arn:aws:sns:eu-west-1:476912836688:sftp_drop_topic",
                "type": "Notification",
                "subject": "Amazon S3 Notification",
            },
        },
    }
