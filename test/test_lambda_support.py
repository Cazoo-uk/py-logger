from io import StringIO
import json
import logging
import os

import cazoo_logger
from cazoo_logger import add_logging_level
from cazoo_logger import lambda_support as ls
from . import LambdaContext
from pytest import raises

from test.pii_cleaner import PiiFilter


def test_invalid_context_fails():
    event = {"My Fake Event": "data"}
    context = {"My Fake Context": "data"}
    context_type = "bad"

    with raises(Exception):
        ls.LoggerProvider().init_logger(event, context, context_type)


def test_decorated_function_creates_logs():
    event = {"source": "test_event", "detail-type": "test event", "id": "12345"}

    request_id = "abc-123"
    function_name = "testing-the-decorator"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    stream = StringIO()

    @ls.exception_logger("cloudwatch")
    def handler(event, context, logger):
        cazoo_logger.config(stream)
        logger.info("Logging a test message", extra={"vrm": "LP12 KZM"})

        return "Hello world"

    assert handler(event, ctx) == "Hello world"

    result = json.loads(stream.getvalue())
    assert result["msg"] == "Logging a test message"
    assert result["data"]["vrm"] == "LP12 KZM"
    assert result["level"] == "info"


def test_add_logging_level():
    event = {"source": "test_event", "detail-type": "test event", "id": "12345"}

    request_id = "abc-123"
    function_name = "testing-the-decorator"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    stream = StringIO()

    os.environ["LOG_LEVEL"] = "TRACE"
    add_logging_level("TRACE", 15)

    @ls.exception_logger("cloudwatch")
    def handler(event, context, logger):
        cazoo_logger.config(stream, level=os.environ["LOG_LEVEL"])
        logger.trace("Logging a test message", extra={"vrm": "LP12 KZM"})
        return "Hello world"

    assert handler(event, ctx) == "Hello world"

    # CLEAN UP THE NEW LOG LEVEL SO IT DOESN'T LEAK INTO OTHER TESTS
    delattr(logging, "TRACE")

    result = json.loads(stream.getvalue())

    assert result["msg"] == "Logging a test message"
    assert result["data"]["vrm"] == "LP12 KZM"
    assert result["level"] == "trace"


def test_handler_logger_with_filter():
    event = {"source": "test_event", "detail-type": "test event", "id": "12345"}

    request_id = "abc-123"
    function_name = "testing-the-decorator"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    stream = StringIO()

    @ls.handler_logger("cloudwatch", log_filter=PiiFilter)
    def handler(event, context, logger):
        cazoo_logger.config(stream)
        logger.info(
            "Logging a test message",
            extra={"vrm": "LP12 KZM", "email_address": "me@email.com"},
        )

        return "Hello world"

    assert handler(event, ctx) == "Hello world"

    result = json.loads(stream.getvalue())
    assert result["msg"] == "Logging a test message"
    assert result["data"]["vrm"] == "LP12 KZM"
    assert result["level"] == "info"
    assert result["data"] == {"vrm": "LP12 KZM", "email_address": "PII REMOVED"}


def test_handler_logger_removes_pii_empty():
    event = {"source": "test_event", "detail-type": "test event", "id": "12345"}

    request_id = "abc-123"
    function_name = "testing-the-decorator"
    function_version = "brand-new"

    ctx = LambdaContext(request_id, function_name, function_version)
    stream = StringIO()

    @ls.handler_logger("empty", log_filter=PiiFilter)
    def handler(event, context, logger):
        cazoo_logger.config(stream)
        logger.info(
            "Logging a test message",
            extra={"vrm": "LP12 KZM", "email_address": "me@email.com"},
        )

        return "Hello world"

    assert handler(event, ctx) == "Hello world"

    result = json.loads(stream.getvalue())
    assert result["data"] == {"vrm": "LP12 KZM", "email_address": "PII REMOVED"}
