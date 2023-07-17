import logging
from src.logutils.filter import AppFilter
from pythonjsonlogger import jsonlogger


class CustomLogging(object):
    def __init__(self, __name__):

        self.logger = logging.getLogger(__name__)

        syslog = logging.StreamHandler()
        syslog.addFilter(AppFilter())
        syslog.setFormatter(jsonlogger.JsonFormatter())

        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(syslog)

    def info(self, message):
        self.logger.info(message)
