from collections import defaultdict
from functools import lru_cache
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from connexion import problem
from flask import request
from requests.exceptions import ConnectionError

sparql_endpoint = "https://ontopia-virtuoso.agid.gov.it/sparql"


def get_status():
    try:
        res = requests.get(sparql_endpoint)
        status_code = res.status_code
    except ConnectionError as e:
        status_code = 500

    if status_code == 200:
        return {
            "status": 200,
            "title": "Ok",
            "detail": f"Ontology server is running: {sparql_endpoint}",
        }

    return problem(
        status=status_code,
        title="Cannot reach remote server",
        detail=f"Error while communicating with the remote server: {sparql_endpoint}",
    )


@lru_cache(maxsize=50)
def get_vocabulary(classification="classification-for-documents", vocabulary_name="government-documents-types", limit=200, cursor=None, offset=0):
    vocabulary_uri = "https://w3id.org/italia/controlled-vocabulary/" f"{classification}/{vocabulary_name}"
    assert "cursor".isalnum(), "Cursor is not alnum"
    cursor_filter = f'FILTER (?id > "{cursor}")' if cursor is not None else ""
    offset_clause = f"OFFSET {offset}" if offset else ""
    qp = {
        "query": [
            "select ?id ?value where {"
            "?x skos:inScheme "
            f"<{vocabulary_uri}>"
            "; skos:notation ?id;  "
            "skos:prefLabel ?value "
            f" {cursor_filter} "
            "} "
            "ORDER BY ?id "
            f"LIMIT {limit}"
            f" {offset_clause} "
        ],
        "format": ["application/sparql-results+json"],
        "timeout": ["0"],
        "debug": ["on"],
        "run": [" Run Query "],
    }

    ep = urlencode(qp, doseq=True)
    data = requests.get(f"{sparql_endpoint}?" + ep)
    try:
        j = data.json()
    except Exception as e:
        return data.content.decode()

    d = defaultdict(list)
    i = None
    for i, item in enumerate(j["results"]["bindings"]):
        value, _id = item["value"], item["id"]
        lang = value["xml:lang"]
        d[lang].append({_id["value"]: value["value"]})
    offset_next = offset + i + 1 if i is not None and offset is not None else 0
    d["_links"] = {
        "limit": limit,
        "url": vocabulary_uri,
        "query": qp["query"],
        "cursor": _id["value"] if i is not None else None,
        "count": i + 1 if i is not None else 0,
        "offset_next": offset_next,
        "page_next": request.base_url + "?offset=" + str(offset_next)
        if offset_next is not None
        else "",
    }
    return dict(d)


def bar():
    u = """https://ontopia-virtuoso.agid.gov.it/sparql?default-graph-uri=&query=select+%3Fvalue+%3Fid+where+%7B%0D%0A%3Fx+rdf%3Atype+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCPV%2FSex%3E%3B%0D%0A+skos%3Anotation+%3Fid%3B%0D%0A+skos%3AprefLabel+%3Fvalue%0D%0A%7D+LIMIT+200&format=application%2Fsparql-results%2Bjson&timeout=0&debug=on&run=+Run+Query+"""
    url = urlparse(u)
    qp = parse_qs(url.query)
