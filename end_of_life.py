import requests
import json
import sys

def consultar_eol(tecnologia: str) -> dict:
    url = f"https://endoflife.date/api/{tecnologia}.json"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    dados = response.json()

    return {
        "tecnologia": tecnologia,
        "versao": dados[0]["cycle"],
        "fim_suporte": dados[0]["eol"]
    }

if __name__ == "__main__":
    try:
        resultado = consultar_eol("python")
        print(json.dumps(resultado, indent=2))
    except Exception as e:
        print(json.dumps({"erro": str(e)}))
        sys.exit(1)
