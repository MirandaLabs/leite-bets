@echo off
REM Script para rodar o scraper local no Windows

echo ========================================
echo 🏠 Iniciando Scraper Local (sem proxy)
echo ========================================
echo.

REM Verifica se .env.local existe
if not exist .env.local (
    echo ❌ Arquivo .env.local não encontrado!
    pause
    exit /b 1
)

echo ✅ Carregando variáveis de ambiente...
echo.

REM Executa o scraper
python scrapers\local\run_all_local.py

echo.
echo ========================================
echo ✅ Coleta finalizada!
echo ========================================
pause
