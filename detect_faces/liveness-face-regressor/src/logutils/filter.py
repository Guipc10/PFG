import logging
from src.logutils.middlewares import get_request_id


class AppFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True
