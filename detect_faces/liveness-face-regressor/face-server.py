#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import traceback
import logging
from functools import wraps
from flask import Flask, g, has_request_context, request
from src.model.regression import Regressor
from src.model.util.arguments import ServerArgs
from timeit import default_timer as timer
from src.MostElasticsearchTracingLib.lib import log
from src.MostElasticsearchTracingLib.lib import es_trace
import logging

#
# Routes
#

def create_app():
    app = Flask(__name__)
    gunicorn_info_logger = logging.getLogger('gunicorn.info')
    app.logger.handlers.extend(gunicorn_info_logger.handlers)
    app.logger.setLevel(logging.INFO)

    return app

app = create_app()

args = ServerArgs()
face_detection = Regressor(args)


if es_trace.conf.ELASTIC_APM_SERVER_URL:
    es_trace.config_app(app)


def get_flask_request_id():
    """
    Returns the Id of the request received. If there is no a request Id, or if it is not a request context, returnts a empty string.
    """
    if has_request_context():
        return request.headers.get("Param-Request-Id", "")
    else:
        return ""


def put_errs(f):
    @wraps(f)
    def put_errs_wrapper(*args, **kwargs):
        """
        Add the 'errs' label to the response in case there is no errs in it, and add the errors in the errs label, in case there is erros to add.
        """
        r, r_code = f(*args, **kwargs)

        # in case there is no errs field in the response
        if "errs" not in r:
            r["errs"] = []

        # In case there is no error to add
        if "errs" not in g:
            return r, r_code

        # In case there is erros to add (return 500 by default)
        for err in g.errs:
            r["errs"].append(err)

        return r, 500

    return put_errs_wrapper


def put_req_id(f):
    @wraps(f)
    def put_req_id_wapper(*args, **kwargs):
        """
        Returns the response in case there is a request Id. If there is not, add a request id to the response.
        """
        r, r_code = f(*args, **kwargs)

        if "request_id" in r:
            return r, r_code

        req_id = get_flask_request_id()

        if not req_id:
            return r, r_code

        r["request_id"] = req_id

        return json.dumps([r]), r_code

    return put_req_id_wapper


def parse_images(request):
    """
    Read and return a list with de images received in the request.
    """
    images = request.files.getlist("images")
    images = [image.read() for image in images]
    return images


@app.route("/", methods=["GET"])
@put_req_id
def healthcheck():
    """
    If the route is working, returns a 'healthy!' string.
    """
    return "healthy!", 200


@app.route("/regress-face", methods=["POST"])
@put_req_id
@put_errs
def regress_face():
    """
    Returns a response object with the prediction from the face regression or an error after receive the request and trying to make the predictions
    or due to a empty list or some problem in parse_images.
    """
    logger = log.get_logger("regress-face")
    logger.info("Request Received")

    if request.files.getlist("images") == []:
        return {"err": "Empty List or None object is not acceptable"}, 422

    try:
        images = parse_images(request)
    except:
        logger.error("Exception raised: {}".format(traceback.format_exc()))
        return {"err": traceback.format_exc()}, 500

    if images is None:
        logger.info("Image key not found in request")
        return {"error": "Image key not found in request"}, 422

    try:
        start = timer()
        response = face_detection.detect(images, logger)
        end = timer()
        logger.info("Took {} seconds".format(end - start))
        logger.info("Finished")
        return response, 200
    except:
        logger.error("Exception raised: {}".format(traceback.format_exc()))
        return {"err": traceback.format_exc()}, 500


if __name__ == "__main__":  # pragma: no cover

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 4010)),
        threaded=False,
        debug=True,
    )
