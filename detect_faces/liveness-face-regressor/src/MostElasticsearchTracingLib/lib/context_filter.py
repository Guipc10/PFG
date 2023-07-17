import logging

from .logging_context import logging_context_handler


class ContextFilter(logging.Filter):
    def __init__(self):
        super(ContextFilter, self).__init__()

    def filter(self, record):
        # print(logging_context_handler)
        req_id = logging_context_handler.get("request_id")
        if req_id is None:
            req_id = 'no-req-id'

        record.req_id = req_id

        return True
