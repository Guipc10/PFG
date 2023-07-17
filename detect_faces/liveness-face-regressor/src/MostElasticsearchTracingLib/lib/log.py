import os
import logging.config
import structlog
from typing import Optional, Any
from elasticapm.traces import execution_context
from .conf import BaseConfig as conf

if conf.API_PROVIDER == "flask":
    from flask import has_request_context, request

    def _flask_request_id_processor(_, __, event_dict):
        req_id = 'no-req-id'

        if has_request_context() and request.headers:
            h_req_id = request.headers.get('Param-Request-Id', '')

            if h_req_id:
                req_id = h_req_id.split(';')[0]

                if req_id:
                    event_dict['request_id'] = req_id

        return event_dict
    
else:
    from fastapi import Request
    from starlette_context.plugins import Plugin
    from starlette_context import context
    from starlette_context.errors import ContextDoesNotExistError
    from .context_filter import ContextFilter


    class FastAPIRequestIdPlugin(Plugin):
        key = "Param-Request-Id"
        async def process_request(
            self, request: Request
        ) -> Optional[Any]:
            # access any part of the request
            return request.headers.get("param-request-id", 'no-req-id')


    def _fastapi_request_id_processor(_, __, event_dict):
        req_id = 'no-req-id'
        try:
            if context and 'Param-Request-Id' in context:
                h_req_id = context.get('Param-Request-Id', 'no-req-id')
                if h_req_id:
                    req_id = h_req_id.split(';')[0]
                    event_dict['request_id'] = req_id

        except ContextDoesNotExistError:
            event_dict['request_id'] = req_id

        return event_dict

def _elastic_processor(logger, method_name, event_dict):
    """
    Add three new entries to the event_dict for any processed events:

    * transaction.id
    * trace.id
    * span.id

    Only adds non-None IDs.

    :param logger:
        Unused (logger instance in structlog)
    :param method_name:
        Unused (wrapped method_name)
    :param event_dict:
        Event dictionary for the event we're processing
    :return:
        `event_dict`, with three new entries.
    """
    transaction = execution_context.get_transaction()

    if transaction:
        event_dict["transaction.id"] = transaction.id

    if transaction and transaction.trace_parent:
        event_dict["trace.id"] = transaction.trace_parent.trace_id

    span = execution_context.get_span()

    if span and hasattr(span, 'id'):
        event_dict["span.id"] = span.id

    return event_dict

def _config_log(processors):
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name):
    return structlog.get_logger(name)


shared_processors = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt='iso'),
    # structlog.processors.ExceptionPrettyPrinter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    _flask_request_id_processor if conf.API_PROVIDER == "flask" else _fastapi_request_id_processor,
    _elastic_processor
]

structlog_processors = [structlog.stdlib.filter_by_level] + shared_processors
conf.LOG_JSON = True

if conf.LOG_JSON:
    structlog_processors.append(structlog.stdlib.render_to_log_kwargs)
else:
    structlog_processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": shared_processors
        },
        "plain_colored": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": shared_processors
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json" if conf.LOG_JSON else "plain_colored",
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": os.getenv("LOG_LEVEL","INFO"),
            "propagate": True,
        },
    }
}
if conf.API_PROVIDER == 'fastapi':
    config['filters'] = {'req_id_filter': { 'class': 'ContextFilter' }}

logging.config.dictConfig(config)

_config_log(structlog_processors)

# __import__('logging_tree').printout()


#
# Tests
#


if __name__ == "__main__":
    logger = get_logger('Logger Name')
    logger.debug('DEBUG')
    logger.info('INFO')
    logger.warn('WARN')
    logger.warning('WARNING')
    logger.error('ERROR')

    llll = logging.getLogger('TESTE')
    llll.info('asdasdasd')
