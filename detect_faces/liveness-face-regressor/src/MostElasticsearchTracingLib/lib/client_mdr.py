import _thread
import elasticapm
from elasticapm.traces import execution_context
from .request_id_manager import REQ_IDS

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


class ElasticMdrClient(elasticapm.Client):

    def __init__(self, framework_name):
        super(ElasticMdrClient, self).__init__(
            framework_name=framework_name
        )

    def begin_transaction(
            self,
            request_id,
            _type,
            req_ids=None
    ):
        if request_id is not None and  '___' in request_id:
            request_id = request_id.split('___')[0]
        super(ElasticMdrClient, self).begin_transaction(_type)
        transaction = execution_context.get_transaction()
        if req_ids is None:
            req_ids = REQ_IDS()
        req_ids.add_req_id(request_id, transaction)

    def end_transaction(
            self,
            request_id,
            name,
            result,
            req_ids=None
    ):
        if request_id is not None and '___' in request_id:
            request_id = request_id.split('___')[0]
        self.update_transaction(request_id, req_ids=req_ids)
        super(ElasticMdrClient, self).end_transaction(name, result)
        if req_ids is None:
            req_ids = REQ_IDS()
        req_ids.pop_req_id(request_id)

    def update_transaction(self, request_id, req_ids=None):
        if req_ids is None:
            req_ids = REQ_IDS()
        if request_id is not None and  '___' in request_id:
            request_id = request_id.split('___')[0]
        transaction = req_ids.get_transaction(request_id)
        if transaction is not None:
            execution_context.set_transaction(transaction)
            

