# Ontopia Core Vocabularies API

Questa PoC permette di interrogare ontopia
tramite un API REST che recupera i dati dei vocabolari controllati.

## test

Eseguire su un sistema con python

    tox
  
Oppure tramite docker

    docker-compose up test


## Deploy su Docker

Eseguire l'applicazione tramite docker-compose con

    docker-compose up run

## deploy su GCP

L'installazione su GCP avviene col comando

        gcloud app deploy ontopya-api --runtime python38 --project \
         ontopia-api 

che restituisce l'URL di interrogazione

        curl -kv https://us-central1-ontopya-api.appspot.net/vocabolari/v0/ui/


### Tecnologia

L'API è basata sul quickstart di Google App Engine

vedi:

* [Cloud Functions Hello World tutorial][tutorial]
* [Cloud Functions Hello World sample source code][code]

[tutorial]: https://cloud.google.com/functions/docs/quickstart
[code]: main.py

