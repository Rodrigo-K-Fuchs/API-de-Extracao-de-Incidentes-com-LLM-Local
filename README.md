# 🧠 API de Extração de Incidentes com LLM Local (Ollama)

API que recebe textos livres descrevendo incidentes e retorna informações estruturadas em JSON, utilizando um LLM local via Ollama.

---

## 🎯 Objetivo

Demonstrar um pipeline completo de extração de informações com:

- Pré-processamento determinístico de texto
- Extração semântica com LLM local
- Validação estrutural com Pydantic
- API HTTP simples e documentada

Tudo isso sem depender de serviços externos.

---

## 🏗️ Arquitetura

```
Usuário → FastAPI → Pré-processamento → Ollama (LLM) → Pydantic → JSON estruturado
```

1. Usuário envia um texto via API
2. O texto passa por pré-processamento determinístico
3. O texto tratado é enviado ao LLM local (Ollama)
4. O retorno do LLM é validado com Pydantic
5. A API devolve um JSON estruturado

---

## 🧹 Pré-Processamento de Texto

Antes de qualquer chamada ao LLM, o texto passa por regras fixas, previsíveis e testáveis:

- **Normalização** — lowercase e limpeza geral
- **Remoção de acentos**
- **Padronização de datas e horas**
- **Extração de hints temporais**
- **Fuzzy matching** com distância de Levenshtein — corrige pequenas variações de palavras e reduz dependência do LLM

Isso garante maior **consistência**, **reprodutibilidade** e **testabilidade** no pipeline.

---

## 📁 Estrutura do Projeto

```
.
├── api.py                        # Ponto de entrada da API FastAPI
│
├── core/
│   ├── incident_extractor.py     # Orquestra o pipeline (prompt + LLM + parsing)
│   └── text_preprocessor.py     # Pré-processamento determinístico do texto
│
├── model/
│   ├── incident.py               # Modelo Pydantic do incidente
│   └── incident_prompt.py        # Prompt utilizado pelo LLM
│
├── tests/
│   ├── unit/                     # Testes unitários
│   ├── integration/              # Testes de integração
│   └── conftest.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🛠️ Pré-requisitos

Antes de começar, você precisa ter instalado:

- [Docker Desktop](https://docs.docker.com/get-started/introduction/get-docker-desktop/)
- [Git](https://git-scm.com/downloads) ou [GitHub CLI](https://cli.github.com/) *(para clonar o repositório)*

---

## 🚀 Instalação e Configuração

### 1. Instalar o Docker Desktop e Git

Acesse e siga as instruções do instalador para o seu sistema operacional:

👉 https://git-scm.com/install/windows
👉 https://docs.docker.com/get-started/introduction/get-docker-desktop/

Após a instalação, **abra o Docker Desktop** e aguarde ele inicializar completamente (ícone na bandeja do sistema deve ficar verde/estável).

### 2. Clonar o repositório

**Opção A — GitHub CLI (recomendado):**

```bash
gh repo clone Rodrigo-K-Fuchs/API-de-Extracao-de-Incidentes-com-LLM-Local
```

**Opção B — Git padrão:**

```bash
git clone https://github.com/Rodrigo-K-Fuchs/API-de-Extracao-de-Incidentes-com-LLM-Local.git
```

**Opção C — Download ZIP:**

Na página do repositório no GitHub, clique em `Code` → `Download ZIP` e extraia o conteúdo.

---

### 3. Navegar até a pasta do projeto

Após clonar ou extrair o ZIP, acesse a pasta raiz do projeto:

```bash
cd API-de-Extracao-de-Incidentes-com-LLM-Local
```

> ⚠️ **Todos os comandos a seguir devem ser executados a partir desta pasta.**

---

## 🐳 Rodando com Docker

### Build da imagem

```bash
docker build -t incident-api .
```

### Subindo a aplicação

```bash
docker compose up
```
Para encerrar:
CTRL + C
---

## 🌐 Documentação Interativa

Com a aplicação rodando, acesse a interface Swagger para testar a API diretamente no navegador:

```
http://localhost:8000/docs
```

---

## 🧪 Testes

O projeto possui testes unitários (pré-processamento, validações e regras determinísticas) e testes de integração (pipeline completo com LLM mockado).

Para executar os testes, abra o projeto em uma IDE ou editor de texto e, no terminal na raiz do projeto, execute:

```bash
pytest
```

> Os testes de integração utilizam mock do LLM e **não requerem** o Ollama rodando.

---

## ⚠️ Regras do Sistema

- Campos não inferíveis retornam `null`
- Horários impossíveis retornam `"INVALIDO"`
- Nenhuma informação é inventada pelo LLM
- Todo output passa por validação Pydantic
- O LLM não decide sozinho — o código manda

---

## 📖 Documentação no Código

Todas as classes principais possuem docstrings descrevendo responsabilidade, entradas, saídas e comportamento esperado.
