FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tornar os scripts de entrypoint executáveis
RUN chmod +x entrypoint.sh entrypoint-bot.sh entrypoint-railway.sh

# Railway usa PORT dinamicamente (8080 geralmente)
EXPOSE 8000 8080

# Usar script Python robusto que aguarda PostgreSQL e inicia o servidor
CMD ["python", "railway_start.py"]

