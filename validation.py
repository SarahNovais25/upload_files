import subprocess
import sys
import os
import re

LOGSTASH_CMD = "logstash"

def get_modified_conf_files():
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.splitlines()
        return [f for f in files if f.endswith(".conf")]
    except subprocess.CalledProcessError as e:
        print("Erro ao obter arquivos modificados:", e)
        sys.exit(1)

def validate_with_logstash(files):
    try:
        result = subprocess.run(
            [LOGSTASH_CMD, "--log.level", "fatal", "--config.test_and_exit", "-f"] + files,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("❌ Erro(s) de sintaxe detectado(s) pelo Logstash:")
            print(result.stderr.strip())
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Logstash não encontrado. Verifique se está no PATH ou configure o caminho no script.")
        return False

def validate_semantic_errors(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patterns = {
        r"add_field\s*=>\s*{\s*['"]?.+['"]?\s*}": "add_field com valor, mas sem chave (faltando =>)",
        r"add_field\s*=>\s*{\s*}": "add_field => {} vazio",
        r"remove_field\s*=>\s*{\s*}": "remove_field => {} vazio",
        r"mutate\s*{\s*}": "bloco mutate vazio"
    }

    errors = []

    for i, line in enumerate(lines, start=1):
        for pattern, description in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                col = match.start() + 1
                errors.append(f"↳ {file_path}: linha {i}, coluna {col} → {description}")

    return errors

def main():
    modified_files = get_modified_conf_files()
    if not modified_files:
        print("✅ Nenhum arquivo .conf modificado.")
        return

    all_errors = []

    for file_path in modified_files:
        semantic_errors = validate_semantic_errors(file_path)
        if semantic_errors:
            all_errors.extend(semantic_errors)

    if all_errors:
        print("❌ Erro(s) lógico(s) detectado(s):")
        for err in all_errors:
            print(err)
        print("🛑 Corrija os erros acima antes de fazer commit.")
        sys.exit(1)

    print("🚀 Executando validação sintática com Logstash...")
    if not validate_with_logstash(modified_files):
        print("🛑 Corrija os erros de sintaxe acima antes de fazer commit.")
        sys.exit(1)

    print("✅ Todos os arquivos foram validados com sucesso.")

if __name__ == "__main__":
    main()
