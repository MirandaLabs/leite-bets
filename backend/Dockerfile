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

# Usar entrypoint-railway.sh que tem suporte a Railway
ENTRYPOINT ["./entrypoint-railway.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

