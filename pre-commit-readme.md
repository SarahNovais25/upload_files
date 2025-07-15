# 🧠 Projeto de Validação com Logstash + Pre-commit

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
  - [📦 Estrutura esperada](#-estrutura-esperada)
  - [🔧 Dicas úteis](#-dicas-úteis)
  - [🧯 Problemas comuns](#-problemas-comuns)

---

## 🚀 Sobre o projeto

Este projeto valida automaticamente configurações do Logstash com base no conteúdo dos arquivos `.conf`, usando um script Python que roda sempre que você faz um commit no Git.

---

## 🧩 Validação automática com Pre-commit

O `pre-commit` é uma ferramenta que executa scripts automaticamente antes do commit. Aqui, usamos para validar arquivos `.conf` com o Logstash.

### ✅ Requisitos obrigatórios

| Requisito | Descrição | Instalar em |
|----------|-----------|-------------|
| Python 3.7+ | Para rodar o pre-commit | [python.org](https://www.python.org/downloads/) |
| Git | Controle de versão e hooks | [git-scm.com](https://git-scm.com/downloads) |
| Logstash | Para validar os `.conf` com `--config.test_and_exit` | [elastic.co/logstash](https://www.elastic.co/logstash) |

---

### ⚙️ Como configurar

1. (Opcional) Ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
