# Ontopia Core Vocabularies API

Questa PoC permette di interrogare ontopia
tramite un API REST che recupera i dati dei vocabolari controllati.

## test

Eseguire

  tox

## deploy

L'installazione su GCP avviene col comando

        gcloud functions deploy ontopya_get --runtime python37 --project ontopya-api --trigger-http

che restituisce l'URL di interrogazione

        curl -kv https://us-central1-ontopya-api.cloudfunctions.net/ontopya_get


Note: è necessario attivare anche le Build API perché le Cloud Functions vengono eseguite dentro container.

### Tecnologia

L'API è basata sul quickstart di Google Cloud Functions

vedi:

* [Cloud Functions Hello World tutorial][tutorial]
* [Cloud Functions Hello World sample source code][code]

[tutorial]: https://cloud.google.com/functions/docs/quickstart
[code]: main.py

