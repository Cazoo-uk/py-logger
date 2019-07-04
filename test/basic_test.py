import json
import logging
from io import StringIO

import cazoo_logger


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
    logger.info("hello", type='thing-happened')
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
    except:
        logger.exception("Uh oh")

    result = json.loads(stream.getvalue())

    assert result["data"]["error"]["name"] == "ValueError"
    assert result["data"]["error"]["message"] == "What even IS that??"

    assert result["msg"] == "Uh oh"
