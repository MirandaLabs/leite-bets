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

EXPOSE 8000

# Railway: Usar entrypoint-railway.sh se RAILWAY_ENVIRONMENT existir
# Docker Compose: Usar entrypoint.sh
CMD ["sh", "-c", "if [ -n \"$RAILWAY_ENVIRONMENT\" ]; then ./entrypoint-railway.sh; else ./entrypoint.sh; fi && uvicorn main:app --host 0.0.0.0 --port 8000"]

