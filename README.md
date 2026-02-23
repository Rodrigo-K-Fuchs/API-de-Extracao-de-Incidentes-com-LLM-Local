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
│   └── incident_prompt.py       # Prompt utilizado pelo LLM
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

## 🛠️ Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Ollama](https://ollama.com) instalado localmente

> **Atenção:** o Ollama não roda dentro do container. A API apenas se comunica com ele via HTTP.

---

## 🤖 Instalando o Ollama

Após instalar o Ollama, baixe o modelo e inicie o servidor:

```bash
ollama pull llama3.2
ollama serve
```

---

## 🐳 Rodando com Docker

### 1. Build da imagem

```bash
docker build -t incident-api .
```

### 2. Subindo a aplicação

**Opção A — Docker Compose (recomendado)**

```bash
docker compose up
```

**Opção B — Docker Run**

```bash
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=llama3.2 \
  incident-api
```

A API estará disponível em `http://localhost:8000`.

---

## 🌐 Documentação Interativa

Acesse a interface Swagger para testar a API diretamente no navegador:

```
http://localhost:8000/docs
```

---

## 🧪 Testes

O projeto possui testes unitários (pré-processamento, validações e regras determinísticas) e testes de integração (pipeline completo com LLM mockado).

```bash
pytest
```

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
