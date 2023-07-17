import importlib
import sys
sys.path.insert(0, '')
s3_client = importlib.import_module("liveness-tests-s3-client.s3-client.s3_client")

def pytest_sessionstart(session):
    '''
        Função chamada após a criação do objeto session do pytest,
        e executada antes mesmo de coletar as instâncias de teste
    '''
    print('pytest_sessionstart')
    bc = s3_client.BotoClient()
    bc.download()
    bc.unzip()

def pytest_sessionfinish(session, exitstatus):
    '''
        Função chamada logo antes de acabarem todos os testes
    '''
    print('pytest_sessionfinish')
    bc = s3_client.BotoClient()
    bc.remove()
