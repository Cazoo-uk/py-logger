import logging
from collections import ChainMap


class ContextualAdapter(logging.LoggerAdapter):
    def __init__(self, logger, data=None, prelog_hook=None):
        self.context = data
        if prelog_hook is None or callable(prelog_hook):
            self.prelog_hook = prelog_hook
        else:
            raise TypeError("Supplied prelog_hook is not a callable")
        super().__init__(logger, data)

    def with_context(self, **ctx):
        new_ctx = self.context.new_child()
        new_ctx.update({"context": self.run_prelog_hook(ctx)})
        return ContextualAdapter(self.logger, new_ctx)

    def with_data(self, **ctx):
        new_ctx = self.context.new_child()
        new_ctx.update({"data": self.run_prelog_hook(ctx)})
        return ContextualAdapter(self.logger, new_ctx)

    def process(self, msg, kwargs):
        if "extra" in kwargs:
            extra = kwargs["extra"].copy()
            del kwargs["extra"]
            kwargs["extra"] = {"data": extra}
            kwargs["extra"].update(self.context)
        else:
            kwargs["extra"] = self.context

        if "type" in kwargs:
            kwargs["extra"]["type"] = kwargs.pop("type")

        kwargs["extra"] = self.run_prelog_hook(kwargs["extra"])

        return msg, kwargs

    def run_prelog_hook(self, dict_in):
        if self.prelog_hook:
            return self.prelog_hook(dict_in)
        else:
            return dict_in


class LambdaContext(ContextualAdapter):
    def __init__(self, context, data, logger, service=None, prelog_hook=None):
        default = {
            "context": {
                "request_id": context.aws_request_id,
                "function": {
                    "name": context.function_name,
                    "version": context.function_version,
                },
            }
        }
        if service is not None:
            default["context"]["function"]["service"] = service
        default["context"].update(data)
        if service is not None:
            default["context"]["function"]["service"] = service
        super().__init__(logger, ChainMap(default), prelog_hook)


class S3SnsContext(LambdaContext):
    def __init__(self, event, context, logger, service=None, prelog_hook=None):
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
            service,
            prelog_hook,
        )


class CloudwatchContext(LambdaContext):
    def __init__(self, event, context, logger, service=None, prelog_hook=None):
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
            service,
            prelog_hook,
        )
