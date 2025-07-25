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
            lines = result.stderr.strip().splitlines()
            relevant_errors = []
            for line in lines:
                if any(keyword in line.lower() for keyword in ["error", "exception", "could not parse", "expected", "invalid"]):
                    relevant_errors.append(line)
            if relevant_errors:
                print("\n--- Mensagens relevantes ---")
                for err in relevant_errors:
                    print(err)
                print("----------------------------")
            else:
                print("⚠️ Nenhum erro de sintaxe aparente. Pode ser apenas aviso do Java ou Logstash.")
                print("↳ Última linha capturada:")
                print(lines[-1] if lines else "(vazio)")
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Logstash não encontrado. Verifique se está no PATH ou configure o caminho no script.")
        return False

def find_empty_or_invalid_mutate_blocks(content, file_path):
    errors = []
    pattern = re.compile(r"(?i)(mutate\s*{.*?})", re.DOTALL)
    for match in pattern.finditer(content):
        block = match.group(0)
        start_index = match.start()
        line_num = content[:start_index].count("\n") + 1

        if not re.search(r"(add_field|remove_field|gsub|convert|rename|update)", block, re.IGNORECASE):
            errors.append(f"↳ {file_path}: bloco mutate vazio ou inválido iniciado na linha {line_num}")

    return errors
    
def check_unbalanced_braces(content, file_path):
    errors = []
    stack = []
    lines = content.splitlines()

    for i, line in enumerate(lines, start=1):
        for char in line:
            if char == "{":
                stack.append(i)  # Guarda linha de abertura
            elif char == "}":
                if not stack:
                    errors.append(f"↳ {file_path}: chave '}}' extra na linha {i}")
                else:
                    stack.pop()

    if stack:
        for unmatched_line in stack:
            errors.append(f"↳ {file_path}: chave '{{' não fechada iniciada na linha {unmatched_line}")

    return errors


def validate_semantic_errors(file_path):
    errors = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.splitlines()

    # (1) Verificações simples por linha
   line_patterns = {
    # mutate
    r"add_field\s*=>\s*{\s*['\"]?.+['\"]?\s*}": "add_field com valor, mas sem chave (faltando =>)",
    r"add_field\s*=>\s*{\s*}": "add_field => {} vazio",
    r"remove_field\s*=>\s*{\s*}": "remove_field => {} vazio",
    r"rename\s*=>\s*{\s*['\"]?\s*['\"]?\s*=>\s*['\"]?\s*['\"]?\s*}": "rename com chave e valor vazios",
    r"convert\s*=>\s*{\s*[^}\s]+\s*=>\s*['\"]{0,1}\s*['\"]{0,1}\s*}": "convert com tipo vazio",
    r"gsub\s*=>\s*\[\s*['\"]?[^,\]]+['\"]?\s*(,\s*['\"][^'\"]*['\"])?\s*\]": "gsub com parâmetros incompletos",

    # grok
    r"grok\s*{[^}]*match\s*=>\s*{\s*}": "grok com match vazio",

    # date
    r"date\s*{[^}]*match\s*=>\s*\[\s*\]": "date com match vazio",

    # aggregate
    r"aggregate\s*{[^}]*task_id\s*=>\s*[\"']?\s*[\"']?": "aggregate sem task_id",
    r"aggregate\s*{[^}]*map\s*=>\s*{\s*}": "aggregate com map vazio",

    # clone
    r"clone\s*{[^}]*clones\s*=>\s*\[\s*\]": "clone com clones vazio",

    # ruby
    r"ruby\s*{[^}]*code\s*=>\s*['\"]{0,1}\s*['\"]{0,1}": "ruby com code vazio",

    # if (condição)
    r"if\s*\(\s*\)": "if com condição vazia",

    # split
    r"split\s*{[^}]*field\s*=>\s*['\"]{0,1}\s*['\"]{0,1}": "split com field vazio",

    # prune
    r"prune\s*{[^}]*whitelist_names\s*=>\s*\[\s*\]": "prune com whitelist_names vazio",
    r"prune\s*{[^}]*blacklist_names\s*=>\s*\[\s*\]": "prune com blacklist_names vazio",

    # fingerprint
    r"fingerprint\s*{[^}]*source\s*=>\s*['\"]{0,1}\s*['\"]{0,1}": "fingerprint com source vazio",
    r"fingerprint\s*{[^}]*method\s*=>\s*['\"]{0,1}\s*['\"]{0,1}": "fingerprint com method vazio"
}


    for i, line in enumerate(lines, start=1):
        for pattern, description in line_patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                col = match.start() + 1
                errors.append(f"↳ {file_path}: linha {i}, coluna {col} → {description}")

    # (2) Verificação de mutate vazio
    errors.extend(find_empty_or_invalid_mutate_blocks(content, file_path))

    errors.extend(check_unbalanced_braces(content, file_path))

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
