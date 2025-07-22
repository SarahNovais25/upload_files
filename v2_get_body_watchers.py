from elasticsearch_custom import functions_elk
import json
from datetime import datetime
from datetime import datetime
from zoneinfo import ZoneInfo


# =============================
# CONFIG
# =============================

es_db = functions_elk.connect("production", "alma")
es_aa = functions_elk.connect("production", "aa")

INDEX_NAME = "watcher_metadata"
OUTPUT_FILE = "watchers_status_data.py"

# =============================
# UTILITIES
# =============================

def now_sp():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()

def get_watcher_ids(es):
    """Get all watcher IDs"""
    res = es.search(index=".watches", size=10000, query={"match_all": {}})
    return [hit["_id"] for hit in res["hits"]["hits"]]

def extract_fields(es, watcher_id):
    """Extract index, gte, interval"""
    try:
        watch = es.transport.perform_request("GET", f"/_watcher/watch/{watcher_id}").get("watch", {})

        index = watch.get("input", {}).get("search", {}).get("request", {}).get("indices", [None])[0]
        gte = (
            watch.get("input", {}).get("search", {}).get("request", {})
            .get("body", {}).get("query", {}).get("range", {}).get("@timestamp", {}).get("gte")
        )
        interval = watch.get("trigger", {}).get("schedule", {}).get("interval")

        return {"index": index, "gte": gte, "interval": interval}
    except Exception as e:
        print(f"Error extracting watcher {watcher_id}: {e}")
        return None

def get_metadata(es, watcher_id):
    try:
        return es.get(index=INDEX_NAME, id=watcher_id)["_source"]
    except:
        return None

def has_diff(current, meta):
    return (
        current["index"] != meta.get("index") or
        current["gte"] != meta.get("gte") or
        current["interval"] != meta.get("interval")
    )

def save_metadata(es, watcher_id, data):
    """Save or update metadata"""
    body = {
        "index": data["index"],
        "gte": data["gte"],
        "interval": data["interval"],
        "needs_update": data["needs_update"],
        "updated_at": now_sp()
    }
    es.index(index=INDEX_NAME, id=watcher_id, document=body)

# =============================
# ENVIRONMENT PROCESSING
# =============================

def process_env(es, var_name):
    """Process watchers for a specific environment"""
    result = {}
    for wid in get_watcher_ids(es):
        current = extract_fields(es, wid)
        if not current:
            continue

        meta = get_metadata(es, wid)
        current["needs_update"] = True if not meta else has_diff(current, meta)

        result[wid] = current
        save_metadata(es, wid, current)

    return var_name, result

# =============================
# SAVE OUTPUT FILE
# =============================

def save_py_file(data, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Script gerado automaticamente – NÃO EDITAR\n")
        f.write(f"# Atualizado em: {now_sp()}\n\n")
        for name, content in data:
            f.write(f"{name} = ")
            f.write(json.dumps(content, indent=2, ensure_ascii=False))
            f.write("\n\n")
    print(f"✅ File saved: {path}")

# =============================
# MAIN
# =============================

def main():
    output = []
    output.append(process_env(es_db, "status_db"))
    output.append(process_env(es_aa, "status_aa"))
    save_py_file(output, OUTPUT_FILE)

if __name__ == "__main__":
    main()
