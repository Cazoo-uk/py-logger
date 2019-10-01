import json
from io import StringIO

import cazoo_logger
from cazoo_logger import lambda_support as ls
from . import LambdaContext

from pytest import raises


def test_invalid_context_fails():
    event = {"My Fake Event": "data"}
    context = {"My Fake Context": "data"}
    context_type = "bad"

    with raises(Exception):
        ls.LoggerProvider().init_logger(event,
                                             context,
                                             context_type)


def test_decorated_function_creates_logs():
    event = {
        "source": "test_event",
        "detail-type": "test event",
        "id": "12345"
    }

    request_id = "abc-123"
    function_name = "testing-the-decorator"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    stream = StringIO()

    @ls.exception_logger('cloudwatch')
    def handler(event, context, logger):
        cazoo_logger.config(stream)
        logger.info("Logging a test message", extra={
            "vrm": "LP12 KZM"
        })

        return "Hello world"

    assert handler(event, ctx) == "Hello world"

    result = json.loads(stream.getvalue())
    assert result['msg'] == 'Logging a test message'
    assert result['data']['vrm'] == "LP12 KZM"



