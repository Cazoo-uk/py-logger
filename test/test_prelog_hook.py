import json
from io import StringIO

import cazoo_logger
from test.pii_cleaner import find_and_clean_pii
import pytest


def test_standard_pii_removal():
    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty(find_and_clean_pii)
    logger.info(
        "I am logging some data",
        extra={"customer_id": 123, "email_address": "me@email.com"},
    )
    result = json.loads(stream.getvalue())

    assert result["msg"] == "I am logging some data"
    assert result["data"] == {"customer_id": 123, "email_address": "PII REMOVED"}


def test_no_pii_removal():
    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty()
    logger.info(
        "I am logging some data",
        extra={"customer_id": 123, "email_address": "me@email.com"},
    )
    result = json.loads(stream.getvalue())

    assert result["msg"] == "I am logging some data"
    assert result["data"] == {"customer_id": 123, "email_address": "me@email.com"}


def test_data():

    stream = StringIO()
    cazoo_logger.config(stream)

    logger = cazoo_logger.empty(prelog_hook=find_and_clean_pii)
    logger.with_data(
        sql={
            "query": "select * from foo where bar = ?",
            "parameters": [123],
            "email_address": "me@email.com",
            "first_name": "martin",
        }
    ).info("Hello world")

    result = json.loads(stream.getvalue())

    assert result["data"]["sql"]["query"] == "select * from foo where bar = ?"
    assert result["data"]["sql"]["parameters"] == [123]
    assert result["data"]["sql"]["email_address"] == "PII REMOVED"
    assert result["data"]["sql"]["first_name"] == "PII REMOVED"


def test_error_on_non_callable():
    cazoo_logger.config()

    with pytest.raises(TypeError):
        cazoo_logger.empty(prelog_hook="a string")
