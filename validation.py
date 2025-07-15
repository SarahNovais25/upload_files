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
            print(result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Logstash não encontrado. Verifique se está no PATH ou configure o caminho no script.")
        return False

def validate_semantic_errors(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        r"add_field\s*=>\s*{\s*}",         # add_field vazio
        r"remove_field\s*=>\s*{\s*}",      # remove_field vazio
        r"mutate\s*{\s*}"                   # mutate sem conteúdo
    ]

    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"❌ Erro lógico no arquivo {file_path}: padrão inválido `{pattern}`")
            return False
    return True

def main():
    modified_files = get_modified_conf_files()
    if not modified_files:
        print("✅ Nenhum arquivo .conf modificado.")
        return

    semantic_errors = [f for f in modified_files if not validate_semantic_errors(f)]

    if semantic_errors:
        print("🛑 Corrija os erros lógicos antes de fazer commit.")
        sys.exit(1)

    print("🚀 Executando validação sintática com Logstash...")
    if not validate_with_logstash(modified_files):
        print("🛑 Erros de sintaxe detectados pelo Logstash.")
        sys.exit(1)

    print("✅ Todos os arquivos foram validados com sucesso.")

if __name__ == "__main__":
    main()
