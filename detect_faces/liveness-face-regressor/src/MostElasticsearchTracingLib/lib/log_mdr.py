import logging.config

import structlog
from elasticapm.traces import execution_context
from .conf import BaseConfig as conf
import pprint
from .request_id_manager import REQ_IDS
    
def _request_id_processor(logger, __, event_dict):
    req_id = 'no-req-id'

    req_ids = REQ_IDS()
    if req_ids is not None:
        try:
            h_req_id = req_ids.get_req_id()
            if h_req_id is not None:
                event_dict['request_id'] = h_req_id
        except:
            pass

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
        try:
            event_dict["span.id"] = span.id
        except Exception as exc:
            pass

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
    _request_id_processor,
    _elastic_processor
]

structlog_processors = [structlog.stdlib.filter_by_level] + shared_processors

if conf.LOG_JSON:
    structlog_processors.append(structlog.stdlib.render_to_log_kwargs)
else:
    structlog_processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

logging.config.dictConfig({
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
            "level": "DEBUG",
            "propagate": True,
        },
    }
})

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
