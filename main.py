# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import http.client as http_client
import json
import logging
import re

import requests
import yaml
from flask import abort, escape

from ontopia import get_vocabulary

http_client.HTTPConnection.debuglevel = 2
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def problem(
    status=500, title="Interal Server Error", type="about:blank", detail=None, **kwargs
):
    abort(
        status,
        json.dumps(
            dict(status=status, title=title, type=type, detail=detail, **kwargs)
        ),
    )


def _validate_parameters(request, mandatory_or, available=None):
    available = available or []
    available += mandatory_or

    if mandatory_or and not any(x in mandatory_or for x in request.args):
        msg = f"At least one of the following parameter is required: {mandatory_or}"
        logging.error(RuntimeError(msg))
        problem(status=400, title=msg, args=request.path)

    for x in request.args:
        if x not in available:
            msg = f"Parameter not supported: {x}"
            logging.error(RuntimeError(msg))
            problem(status=400, title=msg, args=request.path)
        if not request.args[x].isalnum() or not request.args[x].isascii():
            msg = f"Only alphanumeric ascii characters are allowed for: {x}"
            logging.error(RuntimeError(msg))
            problem(status=400, title=msg, args=request.path)


def vocabulary_get(request, ontology, vocabulary):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    accept = request.headers.get("accept")
    if False and accept != "application/json":
        abort(
            415,
            {
                "title": "Not Acceptable",
                "details": "Supported formats: application/json",
            },
        )
    if request.method != "GET":
        abort(405, dict("Method not allowed", detail="Only GET requests."))
        limit = 200
    _validate_parameters(request, [], ["limit", "cursor", "offset"])
    limit = request.args.get("limit") or 200
    limit = min(limit, 200)
    offset = request.args.get("offset") or None
    cursor = request.args.get("cursor") or None

    ontology = f"{ontology}/{vocabulary}"
    headers = {
        "Cache-Control": "public, max-age=36000",
        "Content-Type": "application/json",
    }
    return (
        json.dumps(get_vocabulary(ontology, limit, offset=offset, cursor=cursor)),
        200,
        headers,
    )


def ontopya_get(request):

    try:
        ontology, vocabulary = request.path.strip("/ ").split("/")

        return vocabulary_get(request, ontology, vocabulary)

    except (ValueError, IndexError, TypeError) as e:
        problem(
            status=404, title="Not Found", detail="Not Implemented", args=request.path
        )
    except RuntimeError as e:
        return {
            "/ontopya/{ontology}/{vocabulary}": "Return a vocabulary.",
        }
