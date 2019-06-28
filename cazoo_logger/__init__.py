import json
import logging
from collections import ChainMap


def json_formatter(obj):
    "request_id"
    return str(obj)


class JsonFormatter(logging.Formatter):
    """AWS Lambda Logging formatter.

    Formats the log message as a JSON encoded string.  If the message is a
    dict it will be used directly.  If the message can be parsed as JSON, then
    the parse d value is used in the output record.
    """

    def __init__(self, **kwargs):
        """Return a JsonFormatter instance.

        The `json_default` kwarg is used to specify a formatter for otherwise
        unserialisable values.  It must not throw.  Defaults to a function that
        coerces the value to a string.

        Other kwargs are used to specify log field format strings.
        """
        datefmt = kwargs.pop("datefmt", None)

        super(JsonFormatter, self).__init__(datefmt=datefmt)
        self.default_json_formatter = kwargs.pop("json_default", json_formatter)

        self._supported = {"msg", "level", "context", "data"}

    def format(self, record):
        record_dict = record.__dict__.copy()
        record_dict["asctime"] = self.formatTime(record, self.datefmt)

        log_dict = {k: v for k, v in record_dict.items() if k in self._supported and v}

        if record.exc_info:
            exc_type, exc, exc_info = record.exc_info
            err = {
                "name": exc_type.__name__,
                "message": str(exc),
                "stack": self.formatException(record.exc_info),
            }

            if not "data" in log_dict:
                log_dict["data"] = {"error": err}
            else:
                log_dict["data"]["error"] = err

        json_record = json.dumps(log_dict, default=self.default_json_formatter)

        if hasattr(json_record, "decode"):  # pragma: no cover
            json_record = json_record.decode("utf-8")

        return json_record


class ContextualAdapter(logging.LoggerAdapter):
    def __init__(self, logger, data=None):
        self.context = data
        super().__init__(logger, data)

    def with_context(self, **ctx):
        new_ctx = self.context.new_child()
        new_ctx.update({"context": ctx})
        return ContextualAdapter(self.logger, new_ctx)

    def with_data(self, **ctx):
        new_ctx = self.context.new_child()
        new_ctx.update({"data": ctx})
        return ContextualAdapter(self.logger, new_ctx)

    def process(self, msg, kwargs):
        if "extra" in kwargs:
            extra = kwargs["extra"].copy()
            del kwargs["extra"]
            kwargs["extra"] = {"data": extra}
            kwargs["extra"].update(self.context)
        else:
            kwargs["extra"] = self.context

        return msg, kwargs


class LambdaContext(ContextualAdapter):
    def __init__(self, context, data, logger):
        default = {
            "context": {
                "request_id": context.aws_request_id,
                "function": {
                    "name": context.function_name,
                    "version": context.function_version,
                },
            }
        }
        default["context"].update(data)
        super().__init__(logger, ChainMap(default))


class SnsContext(LambdaContext):
    def __init__(self, event, context, logger):
        [record] = event["Records"]
        super().__init__(
            context,
            {
                "sns": {
                    "id": record["Sns"]["MessageId"],
                    "type": record["Sns"]["Type"],
                    "topic": record["Sns"]["TopicArn"],
                    "subject": record["Sns"]["Subject"],
                }
            },
            logger,
        )


class CloudwatchContext(LambdaContext):
    def __init__(self, event, context, logger):
        super().__init__(
            context,
            {
                "event": {
                    "source": event["source"],
                    "name": event["detail-type"],
                    "id": event["id"],
                }
            },
            logger,
        )


def config(stream=None):
    console = logging.StreamHandler(stream)
    console.setLevel(logging.DEBUG)
    console.setFormatter(JsonFormatter())
    logging.root.addHandler(console)
    logging.root.setLevel(logging.DEBUG)


def empty():
    return ContextualAdapter(logging.root, ChainMap())


from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
