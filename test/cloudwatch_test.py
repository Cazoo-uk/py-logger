import json
import logging
from io import StringIO

import cazoo_logger
from . import LambdaContext


def test_cloudwatch_context():

    stream = StringIO()
    cazoo_logger.config(stream)

    request_id = "abc-123"
    function_name = "bestest-ever-function"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    event = {
        "account": "123456789012",
        "region": "us-east-2",
        "detail": {},
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "time": "2019-03-01T01:23:45Z",
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/my-schedule"],
    }

    log = cazoo_logger.cloudwatch(event, ctx)
    log.info("hello world")

    result = json.loads(stream.getvalue())

    assert result["context"] == {
        "request_id": request_id,
        "function": {"name": function_name, "version": function_version},
        "event": {"source": "aws.events", "name": "Scheduled Event", "id": event["id"]},
    }
