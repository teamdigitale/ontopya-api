from collections import defaultdict
from functools import lru_cache
from json import JSONDecodeError
from os import environ
from urllib.parse import urlencode

import requests
from connexion import problem
from flask import current_app, request
from requests.exceptions import ConnectionError

sparql_endpoint = environ.get(
    "ONTOPYA_SPARQL_URL", "https://ontopia-virtuoso.agid.gov.it/sparql"
)


def get_status():
    try:
        current_app.logger.info("Testing connection to: %r", sparql_endpoint)
        res = requests.get(sparql_endpoint)
        status_code = res.status_code
    except ConnectionError as e:
        status_code = 503

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
        headers={"Retry-After": 300},
    )


@lru_cache(maxsize=50)
def get_vocabulary(
    classification="classification-for-documents",
    vocabulary_name="government-documents-types",
    limit=200,
    cursor=None,
    offset=0,
):
    vocabulary_uri = (
        "https://w3id.org/italia/controlled-vocabulary/"
        f"{classification}/{vocabulary_name}"
    )
    if not "cursor".isalnum():
        return problem(
            status=400,
            detail="Cursor is not alphanumeric",
            title="Bad Request"
        )
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
    except JSONDecodeError as e:
        current_app.logger.exception(
            "Error parsing a non-json response the following response: %1000r",
            data.content,
        )

        return problem(
            title="Error in Sparql endpoint.",
            status=500,
            detail=f"The sparql endpoint returned a malformed json response.",
            ext={"query": qp["query"]},
        )
    d = defaultdict(list)
    i = None
    for i, item in enumerate(j["results"]["bindings"]):
        value, _id = item["value"], item["id"]
        lang = value["xml:lang"]
        d[lang].append({_id["value"]: value["value"]})
    offset_next = offset + i + 1 if None not in (i, offset) else 0
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
    return dict(d), 200, {"Cache-Control": "public, max-age=3600"}


def get_datasets(limit: int = 200, offset: int = 0):
    """

    :type limit: object
    """
    offset_clause = f"OFFSET {offset}" if offset else ""
    vocabulary_uri = "http://dati.gov.it/onto/dcatapit#Dataset"
    qp = {
        "query": [
            "select distinct ?uri, ?title where {"
            f"?uri rdf:type <{vocabulary_uri}>."
            " OPTIONAL{ ?uri skos:prefLabel ?title } "  # if there's no title, it's ok
            "} "
            f" LIMIT {limit} "
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
    except JSONDecodeError as e:
        current_app.logger.exception(
            "Error parsing a non-json response the following response: %1000r",
            data.content,
        )
        return problem(
            title="Error in Sparql endpoint.",
            status=500,
            detail=f"The sparql endpoint returned a malformed json response.",
            ext={"query": qp["query"]},
        )

    d = defaultdict(list)
    i = None
    for i, item in enumerate(j["results"]["bindings"]):
        uri = item["uri"]["value"]
        title = item.get("title", {"title": uri.split("/")[-1]})
        url = request.base_url + uri.replace(
            "https://w3id.org/italia/controlled-vocabulary", ""
        )

        d["items"].append({"uri": url, "title": title.get("value", "")})
    offset_next = offset + i + 1 if i is not None and offset is not None else 0
    d["_links"] = {
        "limit": limit,
        "references": vocabulary_uri,
        "query": qp["query"],
        "count": i + 1 if i is not None else 0,
        "offset_next": offset_next,
        "page_next": request.base_url + "?offset=" + str(offset_next)
        if offset_next is not None
        else "",
    }
    return dict(d), 200, {"Cache-Control": "public, max-age=3600"}
