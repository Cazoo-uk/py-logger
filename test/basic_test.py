import json
import logging
import os
from io import StringIO

import cazoo_logger
from cazoo_logger import add_logging_level


class LambdaContext(object):
    def __init__(
        self,
        request_id="request_id",
        function_name="my-function",
        function_version="v1.0",
    ):
        self.aws_request_id = request_id
        self.function_name = function_name
        self.function_version = function_version

    def get_remaining_time_in_millis(self):
        return None


def test_standard_interpolation():
    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty()
    logger.info("Hello %s today is a %s day", "world", "good")
    result = json.loads(stream.getvalue())

    assert result["msg"] == "Hello world today is a good day"


def test_type():
    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty()
    logger.info("hello", type="thing-happened")
    result = json.loads(stream.getvalue())

    assert result["type"] == "thing-happened"


def test_data():

    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty()
    logger.with_data(
        sql={"query": "select * from foo where bar = ?", "parameters": [123]}
    ).info("Hello world")

    result = json.loads(stream.getvalue())

    assert result["data"]["sql"]["query"] == "select * from foo where bar = ?"
    assert result["data"]["sql"]["parameters"] == [123]


def test_exceptions():
    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty()

    try:
        raise ValueError("What even IS that??")
    except:  # noqa: E722
        logger.exception("Uh oh")

    result = json.loads(stream.getvalue())

    assert result["level"] == "error"
    assert result["data"]["error"]["name"] == "ValueError"
    assert result["data"]["error"]["message"] == "What even IS that??"

    assert result["msg"] == "Uh oh"


def test_add_log_level():
    add_logging_level("TRACE", 25)

    stream = StringIO()
    cazoo_logger.config(stream)
    logger = cazoo_logger.empty()

    logger.trace("This is a new level log")
    result = json.loads(stream.getvalue())
    print(json.dumps(result))

    # CLEAN UP THE NEW LOG LEVEL SO IT DOESN'T LEAK INTO OTHER TESTS
    delattr(logging, "TRACE")

    assert result["level"] == "trace"


def test_new_log_level_not_logged_if_logging_turned_too_high():
    # Given that the default log level is INFO
    os.environ["LOG_LEVEL"] = "INFO"
    # When a new logging level with a lower value is added
    add_logging_level("TRACE", 15)

    stream = StringIO()
    cazoo_logger.config(stream, level=os.environ["LOG_LEVEL"])
    logger = cazoo_logger.empty()

    # And we log to this new level
    logger.trace("This is a new level log")

    # Then nothing is logged
    result = stream.getvalue()

    # CLEAN UP THE NEW LOG LEVEL SO IT DOESN'T LEAK INTO OTHER TESTS
    delattr(logging, "TRACE")

    assert result == ""
