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

# Create a fake "app" for generating test request contexts.
from werkzeug.exceptions import BadRequest, NotFound

import ontopia


@pytest.fixture(scope="module")
def app():
    return flask.Flask(__name__)


def test_dataset(app):
    with app.test_request_context(path="/vocabolari",):

        data = ontopia.get_datasets()
        raise NotImplementedError


def test_vocabulary(app):
    with app.test_request_context(path="/vocabolari",):
        onto = "classifications-for-documents/government-documents-types"
        data = ontopia.get_vocabulary(onto)

    assert "en" in data, data
    assert data["en"], data


def test_vocabulary_pagination(app):
    onto = "classifications-for-documents/government-documents-types"
    langs = ("en", "it")

    with app.test_request_context(path=f"/vocabolari/{onto}",):
        ret = ontopia.get_vocabulary(onto)
        print(ret)
        offset = 0
        while True:
            r = ontopia.get_vocabulary(onto, limit=5, offset=offset)
            l = r["_links"]["count"]
            if not l:
                break
            offset += l
            all_values = ((lang, x) for lang in langs if lang in r for x in r[lang])
            for lang, x in all_values:
                ret[lang].remove(x)
                print(lang, next(iter(x)))

        for lang in langs:
            assert not r.get(lang, [])
