Intro, in which opinions are had
--------------------------------

Cazoo-Logger is a deeply opinionated structured logger for Python on AWS Lambda, intended as a stopgap for those poor recalcitrant souls who persist in writing Python instead of GETTING WITH THE GOD DAMNED PROGRAMME and writing Typescript, thereby benefitting from the glory of the One True Logging Library, `cazoo logger`_.

Cazoo-Logger owes a debt to `aws_lambda_logger`_ which is both less opinionated, and probaby better suited to your particular use-case than this library. Go check it out.

Basic Usage
-----------

The Cazoo Logger module exposes a single function `config` that sets up the logger for use.

>>> import cazoo_logger
>>> cazoo_logger.config()

By default this configures the root logger at INFO level, writing to a special JSON formatter.

To obtain a logger instance, call the appropriate Context function with your incoming event and context:

>>> def handler(event, context):
...     logger = cazoo_logger.s3(event, context)
...     logger.info('sup?')
...

This will result in well-formatted json messages with a documented schema.

::

  {
      "msg": "sup?",
      "context": {
          "request_id": "abc123",
          "function": {"name": "do-things", "version": "0.1.2.3"},
          "sns": {
              "id": "66591d01-0241-5751-bb17-586e5a6dcf91",
              "topic": "arn:aws:sns:us-east-1:12345678912:bucket-o-stuff",
              "type": "Notification",
              "subject": "Amazon S3 Notification",
          },
      }
  }

If you don't have an AWS context and event, you can construct a logger with no context

>>> logger = cazoo_logger.empty()

Logging Errors
--------------

Logging caught errors is as simple as setting the exc_info kwarg to True on the log call.

>>> try:
...     raise ValueError("What in the heck do you call that?")
... except:
...     logger.warn("I dunno man, looks pretty sketchy to me", exc_info=True)
...
    {"msg": "I dunno man, looks pretty sketchy to me", "data": {"error": {"name": "ValueError", "message": "What in the heck do you call that?", "stack": "Traceback (most recent call last):\n  File \"<stdin>\", line 2, in <module>\nValueError: What in the heck do you call that?"}}}


Logging additional data
-----------------------

You might want to include additional structured data in your logs. Any values you pass to the `extra` kwarg will be json serialised into the `data` section of your log line.

>>> logger.info("I did a query", extra={'sql': {'query': 'select * from table where field = ?', 'parameters': [123] }})
{"msg": "I did a query", "data": {"sql": {"query": "select * from table where field = ?", "parameters": [123]}}}

You can also use the `with_data` method. This method returns a new logger instance with the data section pre-populated.

>>> new_logger = logger.with_data(sql={'query': 'select * from foo where bar = ?', 'parameters':[234]})
>>> new_logger.debug('doin a query')
{"msg": "doin a query", "data": {"sql": {"query": "select * from foo where bar = ?", "parameters": [234]}}}
>>> new_logger.error('oh noes! the query did not work!')
{"msg": "oh noes! the query did not work!", "data": {"sql": {"query": "select * from foo where bar = ?", "parameters": [234]}}}


Logging additional context
--------------------------

Similarly you might want to add more data to the context section of your log event.

>>> new_logger = logger.with_context(request_id='abc-123')
>>> new_logger.info('handling request')
{"msg": "handling request", "context": {"request_id": "abc-123"}}

.. _cazoo logger: https://www.npmjs.com/package/cazoo-logger
.. _aws_lambda_logger: https://pypi.org/project/aws-lambda-logging
