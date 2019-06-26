import json
import logging
from io import StringIO

from cazoo_logger import config, SnsContext, CloudwatchContext

class LambdaContext(object):
    def __init__(self, request_id="request_id", function_name="my-function", function_version="v1.0"):
        self.aws_request_id = request_id
        self.function_name = function_name
        self.function_version = function_version

    def get_remaining_time_in_millis(self):
        return None

def test_basic_fields():

    stream = StringIO()
    config(stream)

    ctx = LambdaContext(
        request_id="abc123",
        function_name="do-things",
        function_version="0.1.2.3"
    )

    logger = SnsContext({}, ctx, logging.getLogger())
    logger.info("Hello world")

    result = json.loads(stream.getvalue())

    assert result == {
        "msg": "Hello world",
        "context": {
            "request_id": "abc123",
            "function": {
                "name": "do-things",
                "version": "0.1.2.3"
            }
        },
    }


def test_data():

    stream = StringIO()
    config(stream)

    logger = SnsContext({}, LambdaContext(), logging.getLogger())
    logger.with_data(sql={"query": "select * from foo where bar = ?", "parameters": [123]}).info("Hello world")

    result = json.loads(stream.getvalue())

    assert result['data']['sql']['query'] == "select * from foo where bar = ?"
    assert result['data']['sql']['parameters'] == [123]


def test_exceptions():
    stream = StringIO()
    config(stream)

    logger = SnsContext({}, LambdaContext(), logging.getLogger())

    try:
        raise ValueError("What even IS that??")
    except:
        logger.exception("Uh oh")

    result = json.loads(stream.getvalue())

    assert result['data']['error']['name'] == "ValueError"
    assert result['data']['error']['message'] == "What even IS that??"

    assert result['msg'] == 'Uh oh'


def test_cloudwatch_context():

    stream = StringIO()
    config(stream)

    request_id = "abc-123"
    function_name = "bestest-ever-function"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    event = {
        'account': '123456789012',
        'region': 'us-east-2',
        'detail': {},
        'detail-type': 'Scheduled Event',
        'source': 'aws.events',
        'time': '2019-03-01T01:23:45Z',
        'id': 'cdc73f9d-aea9-11e3-9d5a-835b769c0d9c',
        'resources': [
            'arn:aws:events:us-east-1:123456789012:rule/my-schedule'
        ]
    }

    log = CloudwatchContext(event, ctx, logging.getLogger())
    log.info("hello world")

    result = json.loads(stream.getvalue())

    assert result['context'] == {
        "request_id": request_id,
        "function": {
            "name": function_name,
            "version": function_version,
        },
        "event": {
            "source": "aws.events",
            "name": "Scheduled Event",
            "id": event['id']
        }
    }
