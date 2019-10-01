import functools
import os
import sys
import traceback

from . import config, cloudwatch, empty
from .contexts import CloudwatchContext, ContextualAdapter


class LoggerProvider:
    """
    Helper class for instantiating the Cazoo Logger
    """
    logger = None

    @staticmethod
    def init_logger(event, context, context_type) -> [CloudwatchContext,
                                                      ContextualAdapter]:
        if LoggerProvider.logger is None:
            if context_type == 'cloudwatch':
                LoggerProvider.logger = cloudwatch(event, context)
            elif context_type == 'empty':
                LoggerProvider.logger = empty()
            else:
                raise Exception("Invalid context type {0}".format(context_type))
        return LoggerProvider.logger

    @staticmethod
    def get_logger() -> [CloudwatchContext, ContextualAdapter]:
        return LoggerProvider.logger


def exception_logger(context_type):
    """
    Decorator for the Lambda handler that will instantiate the logger and log initial
    event state data.
    :param context_type: The context of the incoming cloudwatch event.
    :return:
    """
    def log_decorator(handler):
        @functools.wraps(handler)
        def exception_handler(event, context):
            config(level=os.environ.get('LOG_LEVEL', 'INFO'))
            log = LoggerProvider.init_logger(event, context, context_type=context_type)
            log.info("Logging event data",
                     extra={"event": event})
            try:
                return handler(event, context, log)
            except Exception as e:
                log.exception("Unhandled exception in Lambda",
                              extra={"event": event})
                raise
        return exception_handler
    return log_decorator

