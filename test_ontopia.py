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
from urllib.parse import urlparse, parse_qs

import flask
import pytest
import logging

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
# Create a fake "app" for generating test request contexts.
from werkzeug.exceptions import BadRequest, NotFound

import ontopia


@pytest.fixture(scope="module")
def app():
    return flask.Flask(__name__)


def test_dataset(app):
    with app.test_request_context(path="/vocabolari",):

        data, status_code, headers = ontopia.get_datasets()
        assert len(data['items']) > 30


def test_vocabulary(app):
    onto, vocabulary = "classifications-for-people", "person-title"

    with app.test_request_context(path=f"/vocabolari/{onto}/{vocabulary}",):
        data, status_code, headers = ontopia.get_vocabulary(onto, vocabulary)

    assert "en" in data, data
    assert data["en"], data


def test_vocabulary_pagination(app):
    onto, vocabulary = "classifications-for-culture", "subject-disciplines"
    langs = ("en", "it")

    with app.test_request_context(path=f"/vocabolari/{onto}/{vocabulary}",):
        ret, status_code, headers = ontopia.get_vocabulary(onto, vocabulary)
        log.debug(ret)
        offset = 0
        while True:
            r, status_code, headers = ontopia.get_vocabulary(onto, limit=5, offset=offset)
            l = r["_links"]["count"]
            if not l:
                break
            offset += l
            all_values = ((lang, x) for lang in langs if lang in r for x in r[lang])
            for lang, x in all_values:
                ret[lang].remove(x)
                log.info(lang, next(iter(x)))

        for lang in langs:
            assert not r.get(lang, [])



def bar():
    u = """https://ontopia-virtuoso.agid.gov.it/sparql?default-graph-uri=&query=select+%3Fvalue+%3Fid+where+%7B%0D%0A%3Fx+rdf%3Atype+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCPV%2FSex%3E%3B%0D%0A+skos%3Anotation+%3Fid%3B%0D%0A+skos%3AprefLabel+%3Fvalue%0D%0A%7D+LIMIT+200&format=application%2Fsparql-results%2Bjson&timeout=0&debug=on&run=+Run+Query+"""
    url = urlparse(u)
    qp = parse_qs(url.query)
