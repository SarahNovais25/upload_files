from elasticsearch import Elasticsearch
from elasticsearch_custom import functions_elk  # assumindo que isso já retorna uma conexão
import json

def get_watchers_by_env(env_name, specific_id=None, filters=None, full_body=False):
    """
    Busca watchers por ambiente, com suporte a filtros opcionais e retorno completo.

    :param env_name: Nome do ambiente (ex: 'db', 'aa')
    :param specific_id: ID exato do watcher (opcional)
    :param filters: Dict com filtros como {'interval': '15m', 'gte': 'now-24h/h'} (opcional)
    :param full_body: Boolean - se True, retorna o body inteiro do watcher
    :return: Dicionário com os watchers filtrados
    """

    es = functions_elk.connect("production", env_name)

    if specific_id:
        watch_ids = [specific_id]
    else:
        search = es.search(index=".watches", size=10000, query={"match_all": {}})
        watch_ids = [hit["_id"] for hit in search["hits"]["hits"]]

    valid_watchers = {}

    for watch_id in watch_ids:
        try:
            resp = es.transport.perform_request("GET", f"/_watcher/watch/{watch_id}")
            watch = resp.get("watch", {})

            # Extrair campos esperados
            indices = (
                watch.get("input", {})
                     .get("search", {})
                     .get("request", {})
                     .get("indices")
            )
            gte = (
                watch.get("input", {})
                     .get("search", {})
                     .get("request", {})
                     .get("body", {})
                     .get("query", {})
                     .get("range", {})
                     .get("@timestamp", {})
                     .get("gte")
            )
            interval = watch.get("trigger", {}).get("schedule", {}).get("interval")

            if full_body:
                valid_watchers[watch_id] = watch
            else:
                # Filtro dinâmico
                if filters:
                    match = True
                    for key, value in filters.items():
                        if key == "interval" and interval != value:
                            match = False
                        if key == "gte" and gte != value:
                            match = False
                    if not match:
                        continue

                valid_watchers[watch_id] = {
                    "indices": indices,
                    "gte": gte,
                    "interval": interval
                }

        except Exception as e:
            print(f"Erro no watcher {watch_id}: {e}")

    return dict(sorted(valid_watchers.items()))
