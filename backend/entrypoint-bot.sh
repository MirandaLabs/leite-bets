#!/bin/bash
set -e

echo "🔄 Aguardando API ficar pronta..."
until curl -sf http://api:8000/health > /dev/null; do
  echo "⏳ API ainda não está pronta - aguardando..."
  sleep 3
done

echo "✅ API está pronta!"
echo "🤖 Iniciando bot do Telegram..."

exec "$@"
