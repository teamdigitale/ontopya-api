# Ontopia Core Vocabularies API

Questa PoC permette di interrogare ontopia
tramite un API REST che recupera i dati dei vocabolari controllati.

Potete utilizzarla nelle vostre infrastrutture per riutilizzare i dati erogati
dallo sparql endpoint di Agid in formato json. Ad esempio, potete recuperare
i dati del vocabolario delle tipologie dei documenti pubblici

```
{
  "it": [
    { "1": "Documento albo pretorio"},
    { "2": "Modulistica"},
    { "3": "Documento funzionamento interno"},
    ...
    ]
}
```

o l'elenco delle province con il codice ISTAT

```
{
it: [
  { "001": "Torino" },
  { "002": "Vercelli"},
  { "003": "Novara"},
  ...
}
```


## Test

Eseguire su un sistema con python

    tox
  
Oppure tramite docker

    docker-compose up test


## Configurazione

E' possibile configurare l'applicazione tramite le seguenti variabili
d'ambiente:

    ONTOPYA_SPARQL_URL  # url dell'endpoint sparql da interrogare
    
    
## Deploy su Docker

Eseguire l'applicazione tramite docker-compose con

    docker-compose up run

## Deploy su GCP

L'installazione su GCP avviene col comando

        gcloud app deploy ontopya-api --runtime python38 --project \
         ontopia-api 

che restituisce l'URL di interrogazione

        curl -kv https://us-central1-ontopya-api.appspot.net/vocabolari/v0/ui/


## Deploy all'interno di un'infrastruttura

Per limitare il carico sullo SPARQL engine remoto, se si prevede un utilizzo massivo
di quest'API conviene deployarla all'interno della propria infrastruttura 
dietro una cache HTTP. Eg.

```
User-Agent --> Cache Server --> Ontopya --> Sparql Engine
```

Ontopya implementa comunque un meccanismo di caching interno
- per ora non configurabile (patches are welcome).

### Tecnologia

L'API è basata sul quickstart di Google App Engine

vedi:

* [Cloud Functions Hello World tutorial][tutorial]
* [Cloud Functions Hello World sample source code][code]

[tutorial]: https://cloud.google.com/functions/docs/quickstart
[code]: main.py

