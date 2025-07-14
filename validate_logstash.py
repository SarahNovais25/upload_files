#!/usr/bin/env python3
import subprocess
import sys
import os

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

def validate_file(file_path):
    print(f"🔍 Validando {file_path}")
    result = subprocess.run(["logstash", "--config.test_and_exit", "-f", file_path])
    return result.returncode == 0

def main():
    modified_files = get_modified_conf_files()
    if not modified_files:
        print("✅ Nenhum arquivo .conf modificado.")
        return

    has_errors = False
    for file in modified_files:
        if not validate_file(file):
            print(f"❌ Erro de validação em {file}")
            has_errors = True
        else:
            print(f"✅ {file} validado com sucesso.")

    if has_errors:
        print("🛑 Corrija os erros antes de fazer commit.")
        sys.exit(1)

if __name__ == "__main__":
    main()
