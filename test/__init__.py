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
