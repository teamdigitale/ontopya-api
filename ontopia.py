from collections import defaultdict
from urllib.parse import parse_qs, urlencode, urlparse
from functools import lru_cache

import requests


def get_status():
    return {"status": 200}


@lru_cache(maxsize=5)
def get_vocabulary(onto="CPV/Sex", limit=200, cursor=None):
    onto_url = "https://w3id.org/italia/onto/" f"{onto}"
    assert "cursor".isalnum(), "Cursor is not alnum"
    cursor_filter = f'FILTER (?id > "{cursor}")' if cursor is not None else ""

    qp = {
        "query": [
            "select ?value ?id where {"
            "?x rdf:type " f"<{onto_url}>" "; skos:notation ?id;  "
            "skos:prefLabel ?value "
            f" {cursor_filter} "
            "} "
            "ORDER BY ?id "
            f"LIMIT {limit}"
        ],
        "format": ["application/sparql-results+json"],
        "timeout": ["0"],
        "debug": ["on"],
        "run": [" Run Query "],
    }

    ep = urlencode(qp, doseq=True)
    data = requests.get("https://ontopia-virtuoso.agid.gov.it/sparql?" + ep)
    try:
        j = data.json()
    except Exception as e:
        return data.content.decode()

    d = defaultdict(list)
    for i, item in enumerate(j["results"]["bindings"]):
        value, _id = item["value"], item["id"]
        lang = value["xml:lang"]
        d[lang].append({_id["value"]: value["value"]})
    d["url"] = onto_url
    d["_links"] = {
        "limit": limit,
        "cursor": _id["value"],
        "count": i,
    }
    return dict(d)


def bar():
    u = """https://ontopia-virtuoso.agid.gov.it/sparql?default-graph-uri=&query=select+%3Fvalue+%3Fid+where+%7B%0D%0A%3Fx+rdf%3Atype+%3Chttps%3A%2F%2Fw3id.org%2Fitalia%2Fonto%2FCPV%2FSex%3E%3B%0D%0A+skos%3Anotation+%3Fid%3B%0D%0A+skos%3AprefLabel+%3Fvalue%0D%0A%7D+LIMIT+200&format=application%2Fsparql-results%2Bjson&timeout=0&debug=on&run=+Run+Query+"""
    url = urlparse(u)
    qp = parse_qs(url.query)
