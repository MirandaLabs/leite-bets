#!/bin/bash

# Script para rodar o scraper local sem proxy

echo "🏠 Iniciando Scraper Local (sem proxy)"
echo "=================================="
echo ""

# Carrega variáveis de ambiente
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo "✅ Variáveis de ambiente carregadas"
else
    echo "❌ Arquivo .env.local não encontrado!"
    exit 1
fi

# Verifica se API_URL está configurada
if [ -z "$API_URL" ]; then
    echo "❌ API_URL não configurada no .env.local!"
    exit 1
fi

echo "📡 Enviando dados para: $API_URL"
echo ""

# Executa o scraper
python3 scrapers/local/run_all_local.py

echo ""
echo "=================================="
echo "✅ Coleta finalizada!"
