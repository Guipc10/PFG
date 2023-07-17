#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os


def env_bool(env_var_name, default=False):
    v = os.getenv(env_var_name, None)
    if v:
        return v.strip().lower() == 'true'

    return default

def flask_or_fastapi():
    try:
        import fastapi
        fastapi = True
    except ModuleNotFoundError:
        fastapi = False

    try:
        import flask
        flask = True
    except ModuleNotFoundError:
        flask = False

    assert int(flask)+int(fastapi)==1, "Flask and FastAPI are installed. Choose one."
    assert flask or fastapi

    if flask:
        return 'flask'

    return 'fastapi'

class BaseConfig:
    # General Config
    LOG_JSON           = env_bool('LOG_JSON', False)
    API_PROVIDER              = flask_or_fastapi()
    ELASTIC_APM_SERVICE_NAME  = os.environ.get('ELASTIC_APM_SERVICE_NAME', 'MostService')
    ELASTIC_APM_SERVER_URL    = os.environ.get('ELASTIC_APM_SERVER_URL', '')
    ELASTIC_APM_ENVIRONMENT   = os.environ.get('ELASTIC_APM_ENVIRONMENT', 'Development')
    ELASTIC_APM_USE_STRUCTLOG = env_bool('ELASTIC_APM_USE_STRUCTLOG', True)
    ELASTIC_APM_DISABLE_LOG_RECORD_FACTORY = env_bool(
        'ELASTIC_APM_DISABLE_LOG_RECORD_FACTORY', True
    )
