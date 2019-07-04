import json
import logging


def json_formatter(obj):
    "request_id"
    return str(obj)


class JsonFormatter(logging.Formatter):
    """AWS Lambda Logging formatter."""

    def __init__(self, **kwargs):
        """Return a JsonFormatter instance.

        The `json_default` kwarg is used to specify a formatter for otherwise
        unserialisable values.  It must not throw.  Defaults to a function that
        coerces the value to a string.
        """
        datefmt = kwargs.pop("datefmt", None)

        super(JsonFormatter, self).__init__(datefmt=datefmt)
        self.default_json_formatter = kwargs.pop("json_default", json_formatter)

        self._supported = {"level", "context", "data", "type"}

    def format(self, record):
        record_dict = record.__dict__.copy()
        record_dict["asctime"] = self.formatTime(record, self.datefmt)

        log_dict = {k: v for k, v in record_dict.items() if k in self._supported and v}
        log_dict["msg"] = record.getMessage()

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
