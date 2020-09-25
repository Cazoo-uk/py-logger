"""
LAMBDA SUPPORT
This module provides useful functions for implementing the logger in Lambda functions.

LoggerProvider
A wrapper class that allows the logger to be easily instantiated and pulled into code
init_logger - will create a logger instance if one does not already exist
get_logger - will retrieve an existing logger instance

exception_logger
Is used as a decorator on the root Lambda Handler in a Lambda function. The function
will create an instance of the logger and then log the incoming event data.

If there are any unhandled exceptions when the handler is run then the Exception detail
is logged.  The Exception is still raised to ensure that the Lambda is correctly marked
as a failure

handler_logger
Is used as a decorator on the root Lambda Handler in a Lambda function. The function
will create an instance of the logger and then log the incoming event data.

Accepts a prelog_hook function that will be applied to all additional data logged
e.g. this can be used to remove any PII that is accidentally logged
"""

import functools
import os

from . import config, cloudwatch, empty
from .contexts import CloudwatchContext, ContextualAdapter


class LoggerProvider:
    """
    Helper class for instantiating the Cazoo Logger.  This will be called when the new
    handler decorator is fired, and so we want to ensure that the logger is reset each
    time.
    """

    logger = None

    @staticmethod
    def init_logger(
        event, context, context_type, prelog_hook=None
    ) -> [CloudwatchContext, ContextualAdapter]:

        config(level=os.environ.get("LOG_LEVEL", "INFO"))
        if context_type == "cloudwatch":
            LoggerProvider.logger = cloudwatch(event, context, prelog_hook=prelog_hook)
        elif context_type == "empty":
            LoggerProvider.logger = empty(prelog_hook=prelog_hook)
        else:
            raise Exception("Invalid context type {0}".format(context_type))
        return LoggerProvider.logger

    @staticmethod
    def get_logger() -> [CloudwatchContext, ContextualAdapter]:
        return LoggerProvider.logger


def exception_logger(context_type, has_pii=False):
    """
    Decorator for the Lambda handler that will instantiate the logger and log initial
    event state data.
    :param context_type: The context of the incoming cloudwatch event.
    :param has_pii: Flag to disable blanket event login for cases where events hold
                    pii data that cannot be logged to cloudwatch
    """

    def log_decorator(handler):
        @functools.wraps(handler)
        def exception_handler(event, context):
            log = LoggerProvider.init_logger(event, context, context_type=context_type)
            if not has_pii:
                log.info("Logging event data", extra={"event": event})
            try:
                return handler(event, context, log)
            except Exception:
                extra = {}
                if not has_pii:
                    extra["event"] = event
                log.exception("Unhandled exception in Lambda", extra=extra)
                raise

        return exception_handler

    return log_decorator


def handler_logger(context_type, prelog_hook=None):
    """
    Decorator for the Lambda handler that will instantiate the logger and log initial
    event state data.
    :param context_type: The context of the incoming cloudwatch event.
    :param prelog_hook: An optional function that will be used to scrub all logged
                        fields of any PII. NB this does NOT apply to the log message
                        itself
    """

    def log_decorator(handler):
        @functools.wraps(handler)
        def exception_handler(event, context):
            log = LoggerProvider.init_logger(
                event, context, context_type=context_type, prelog_hook=prelog_hook
            )
            log.info("Logging event data", extra={"event": event})
            try:
                return handler(event, context, log)
            except Exception:
                log.exception("Unhandled exception in Lambda", extra=event)
                raise

        return exception_handler

    return log_decorator
