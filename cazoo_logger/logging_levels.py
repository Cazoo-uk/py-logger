import logging
from .contexts import ContextualAdapter


def add_logging_level(level_name, level_num):
    """
    Adapted from https://stackoverflow.com/a/35804945
    (Which is to say, shamelessly stolen and tidied up a bit)

    This function will add an additional logging level
    """
    method_name = level_name.lower()
    if hasattr(logging, level_name) and logging.__dict__[level_name] != level_num:
        raise AttributeError(
            "{} already defined in logging module at level {}".format(
                level_name, logging.__dict__[level_name]
            )
        )

    def log_func(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def add_log(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_func)
    setattr(logging, method_name, add_log)

    def log_class_method(self, message, *args, **kwargs):
        self.log(level_num, message, *args, **kwargs)

    setattr(ContextualAdapter, method_name, log_class_method)
