from .conf import BaseConfig as conf


from elasticapm.traces import execution_context



# Shutting up elastic_apm logs
import logging
apm_logger = logging.getLogger('elasticapm')
apm_logger.setLevel(logging.WARNING)
urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.setLevel(logging.WARNING)
sched_logger = logging.getLogger('apscheduler.scheduler')
sched_logger.setLevel(logging.WARNING)
sched_logger_2 = logging.getLogger('apscheduler.executors.default')
sched_logger_2.setLevel(logging.WARNING)
root_logger = logging.getLogger('root')
root_logger.setLevel(logging.ERROR)


class ClientWrapper:
    apm_client = None

    def __getattr__(self, name):
        # Returns a dummy function if the client wasn't instantiated

        if ClientWrapper.apm_client:
            return ClientWrapper.apm_client.__getattribute__(name)
        else:
            return lambda *args, **kwargs: None

    def begin_transaction(self, *args, **kwargs):
        if ClientWrapper.apm_client:
            self.parent_transaction = execution_context.get_transaction()
            ClientWrapper.apm_client.begin_transaction(*args, **kwargs)

    def end_transaction(self, *args, **kwargs):
        if ClientWrapper.apm_client:
            ClientWrapper.apm_client.end_transaction(*args, **kwargs)
            execution_context.set_transaction(self.parent_transaction)


apm    = None
client = ClientWrapper()


def config_app(app):
    global apm
    if conf.API_PROVIDER == 'flask':
        from elasticapm.contrib.flask import ElasticAPM
        app.config['ELASTIC_APM'] = {
            'SERVICE_NAME':               conf.ELASTIC_APM_SERVICE_NAME,
            'SERVER_URL':                 conf.ELASTIC_APM_SERVER_URL,
            'ELASTIC_APM_ENVIRONMENT':    conf.ELASTIC_APM_ENVIRONMENT,
            'ELASTIC_APM_USE_STRUCTLOG':  conf.ELASTIC_APM_USE_STRUCTLOG,
            'DISABLE_LOG_RECORD_FACTORY': conf.ELASTIC_APM_DISABLE_LOG_RECORD_FACTORY
        }

        apm                      = ElasticAPM(app)
        ClientWrapper.apm_client = apm.client
    elif conf.API_PROVIDER == 'fastapi':
        from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
        apm = make_apm_client({
            'SERVICE_NAME':               conf.ELASTIC_APM_SERVICE_NAME,
            'SERVER_URL':                 conf.ELASTIC_APM_SERVER_URL,
            'ELASTIC_APM_ENVIRONMENT':    conf.ELASTIC_APM_ENVIRONMENT,
            'ELASTIC_APM_USE_STRUCTLOG':  conf.ELASTIC_APM_USE_STRUCTLOG,
            'DISABLE_LOG_RECORD_FACTORY': conf.ELASTIC_APM_DISABLE_LOG_RECORD_FACTORY,
            "DEBUG": True,
        })
        app.add_middleware(ElasticAPM, client=apm)
