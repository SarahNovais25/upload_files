# 🧠 Projeto de Validação com Logstash - Pre-commit

Este projeto utiliza `pre-commit` para validar automaticamente arquivos `.conf` do Logstash antes de cada commit. Isso ajuda a evitar que arquivos com erro sejam versionados por engano.

---

## 📚 Sumário

- [📚 Sumário](#-sumário)
- [🚀 Sobre o projeto](#-sobre-o-projeto)
- [🧩 Validação automática com Pre-commit](#-validação-automática-com-pre-commit)
  - [✅ Requisitos obrigatórios](#-requisitos-obrigatórios)
  - [⚙️ Como configurar](#-como-configurar)
  - [🧪 Como funciona o hook](#-como-funciona-o-hook)
  - [📋 Arquivos envolvidos](#-arquivos-envolvidos)

---

## 🚀 Sobre o projeto

Este projeto valida automaticamente configurações do Logstash com base no conteúdo dos arquivos `.conf`, usando um script Python que roda sempre que você faz um commit no Git.

---

## 🧩 Validação automática com Pre-commit

O `pre-commit` é uma ferramenta que executa scripts automaticamente antes do commit. Aqui, usamos para validar arquivos `.conf` com o Logstash.

> ⚠️ **Observação importante:**  
> Se ocorrer erro ao instalar o `pre-commit`, crie um ambiente virtual com Python e ative antes de instalar:
>
> ```bash
> python -m venv .venv
> source .venv/bin/activate       # Windows: .venv\Scripts\activate
> pip install pre-commit
> ```

---

### ✅ Requisitos obrigatórios

| Requisito | Descrição | Instalar em |
|----------|-----------|-------------|
| Python 3.7+ | Para rodar o pre-commit | [python.org](https://www.python.org/downloads/) |
| Git | Controle de versão e hooks | [git-scm.com](https://git-scm.com/downloads) |
| Logstash | Para validar os `.conf` com `--config.test_and_exit` | [elastic.co/logstash](https://www.elastic.co/logstash) |

---

### ⚙️ Como configurar

Instale o `pre-commit`:

```bash
pip install pre-commit
```

Instale os hooks do repositório:

```bash
pre-commit install
```

Esse comando adiciona um *hook* no Git que será executado automaticamente em cada `git commit`.

---

### 🧪 Como funciona o hook

Você edita ou adiciona um arquivo `.conf` dentro do repositório .ce executa:

```bash
git add nome.conf
git commit -m "minha mensagem"
```

O `pre-commit` irá:

- Verificar os arquivos `.conf` modificados
- Rodar `logstash --config.test_and_exit` com nível `fatal` (ocultando `info`, `warn`)
- **Bloquear o commit se houver erro de validação**

---

### 📋 Arquivos envolvidos

#### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-logstash
        name: Validate Logstash .conf files
        entry: python scripts/validate_logstash.py
        language: system
        types: [file]
        files: \.conf$
```

#### `scripts/validate_logstash.py`

Esse script detecta arquivos `.conf` modificados e executa:

```bash
logstash --log.level fatal --config.test_and_exit -f arquivo.conf
```

Você também pode executá-lo manualmente com:

```bash
python scripts/validate_logstash.py
```
