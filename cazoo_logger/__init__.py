import logging
from ._version import get_versions
from .formatters import JsonFormatter
from . import contexts
from collections import ChainMap

__version__ = get_versions()["version"]
del get_versions

__all__ = ["empty", "s3", "cloudwatch", "config"]


def s3(event, context):
    """
    Build a contextual logger for an S3 SNS notification.
    """
    return contexts.S3SnsContext(event, context, logging.root)


def cloudwatch(event, context):
    """
    Build a contextual logger for a Cloudwatch event
    """
    return contexts.CloudwatchContext(event, context, logging.root)


def config(stream=None, level=logging.INFO, boto_level=logging.WARN):
    stdout = logging.StreamHandler(stream)
    stdout.setLevel(level)
    stdout.setFormatter(JsonFormatter())
    logging.root.setLevel(level)
    logging.root.handlers.clear()
    logging.root.addHandler(stdout)
    logging.getLogger("boto").setLevel(boto_level)
    logging.getLogger("botocore").setLevel(boto_level)
    logging.getLogger("boto3").setLevel(boto_level)


def empty():
    """
    Return an empty logger, for use in unit tests or non-lambda envs.
    """
    return contexts.ContextualAdapter(logging.root, ChainMap())
