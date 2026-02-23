# Imagem base estável
FROM python:3.12-slim

# Evita bytecode e buffer estranho
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Dependências primeiro (cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Porta da API
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]