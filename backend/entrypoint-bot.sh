#!/bin/bash
set -e

echo "🤖 Iniciando serviço Bot do Telegram..."

# Não aguarda API se estiver no Railway (serviços independentes)
if [ -z "$RAILWAY_ENVIRONMENT" ]; then
    echo "🔄 Aguardando API ficar pronta (ambiente local)..."
    until curl -sf http://api:8000/health > /dev/null 2>&1; do
      echo "⏳ API ainda não está pronta - aguardando..."
      sleep 3
    done
    echo "✅ API está pronta!"
fi

echo "✅ Iniciando bot com health check server..."

exec "$@"
