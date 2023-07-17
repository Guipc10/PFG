import os
import _thread
from threading import Lock
import pprint

class REQ_IDS(object):

    __instance = None

    def __new__(cls):
        if REQ_IDS.__instance is None:
            REQ_IDS.__instance = object.__new__(cls)
            REQ_IDS.__instance.ids = {}
            REQ_IDS.__instance.lock = Lock()
            REQ_IDS.__instance.map_threads_ids = {}
        return REQ_IDS.__instance

    def len(self):
        return len(self.ids)
    
    def add_req_id(self, req_id, transaction):
        pid = os.getpid()
        tid = _thread.get_ident()
        with self.lock:
            if not req_id in self.ids:
                self.ids[req_id] = {
                    'pids': [pid],
                    'tids': [tid],
                    'transaction': transaction,
                }
                self.map_threads_ids[tid] = req_id
            else:
                pass
                #raise RuntimeError('Request ID already has an ongoing transaction.')

    def get_req_id(self):
        pid = os.getpid()
        tid = _thread.get_ident()
        return self.map_threads_ids.get(tid, None)
                
        
    def pop_req_id(self, req_id):
        with self.lock:
            if req_id in self.ids:
                for tid in self.ids[req_id]['tids']:
                    if tid in self.map_threads_ids:
                        self.map_threads_ids.pop(tid)
                return self.ids.pop(req_id)
        return None


    def get_transaction(self, req_id):
        pid = os.getpid()
        tid = _thread.get_ident()
        with self.lock:
            req_id_info = self.ids.get(req_id, None)
            if req_id_info is not None:
                if not pid in req_id_info['pids']:
                    req_id_info['pids'].append(pid)
                if not tid in req_id_info['tids']:
                    req_id_info['tids'].append(tid)
                self.map_threads_ids[tid] = req_id
                return req_id_info['transaction']
        return None
