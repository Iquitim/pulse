# Use a base oficial de Python compacta
FROM python:3.12-slim

# Evita que o Python grave arquivos .pyc e bufferize a saída
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala ferramentas essenciais para compilação de pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto para o contêiner
COPY . .

# Exponha a porta do FastAPI
EXPOSE 8000

# Executa o servidor Uvicorn com host 0.0.0.0 e porta 8000
CMD ["python", "app.py"]
