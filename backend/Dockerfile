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

# Iniciar direto sem entrypoint complexo
# As migrações serão feitas no startup da aplicação via lifespan
CMD ["sh", "-c", "python -c 'from models import Base, engine; Base.metadata.create_all(engine)' && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

