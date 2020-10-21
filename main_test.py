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

import flask
import pytest

import main
import yaml

# Create a fake "app" for generating test request contexts.
from werkzeug.exceptions import BadRequest, NotFound


TEST_CF = "RSSMRO54P05E472I"


@pytest.fixture(scope="module")
def app():
    return flask.Flask(__name__)




def test_ontopia_get(app):
    o = "CPV"
    v = "Sex"
    with app.test_request_context(path=f"/{o}/{v}",):
        res = main.ontopya_get(flask.request)
        data = yaml.safe_load(res)

        assert "en" in data, data
        assert data["en"], data


def test_onto_NotImplemented(app):
    with app.test_request_context(path="/foo",):
        with pytest.raises(NotFound) as exc:
            res = main.ontopya_get(flask.request)
        assert "Not Implemented" in exc.value.description


def test_ontopya_get(app):
    with app.test_request_context(headers={"accept": "application/json"},
        path='CPV/Sex'
    ):
        res = main.ontopya_get(flask.request)
        assert "en" in res, res


def test_ontopya_get_empty_json(app):
    with app.test_request_context(json="",         path='CPV/Sex'
):
        with pytest.raises(BadRequest) as exc:
            res = main.ontopya_get(flask.request)
        assert "At least one of the following parameter" in exc.value.description


def test_ontopya_get_xss(app):
    with app.test_request_context(        path='"<script>alert(1)</script>"'
,
        query_string={"surname": "<script>alert(1)</script>"}
    ):
        with pytest.raises(BadRequest) as exc:
            res = main.ontopya_get(flask.request)
        # Should be ascii error in description.
        assert "ascii" in exc.value.description
