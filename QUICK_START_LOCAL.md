# 🚀 Guia Rápido - Scrapers Locais

## ⚡ Início Rápido

### 1. Configure o .env.local

```bash
# Edite o arquivo .env.local e configure:
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Execute os scrapers

**Windows (PowerShell/CMD):**
```bash
python scrapers\local\run_all_local.py
```

**Ou use o script batch:**
```bash
run_local_scraper.bat
```

**Linux/Mac:**
```bash
python scrapers/local/run_all_local.py
```

**Ou use o script bash:**
```bash
chmod +x run_local_scraper.sh
./run_local_scraper.sh
```

---

## 📊 O que acontece?

1. ✅ Scraper acessa cada casa de apostas (sem proxy)
2. ✅ Coleta odds de Double Chance do Brasileirão
3. ✅ Envia dados para a API no Railway
4. ✅ API salva no banco PostgreSQL

---

## 🏠 Vantagens da Versão Local

- 🚀 **Mais rápida** - Sem overhead de proxy
- 💰 **Gratuita** - Usa sua internet normal
- 🔧 **Fácil debug** - Logs detalhados
- 🎯 **Ideal para dev** - Testes rápidos

---

## ⚙️ Scrapers Disponíveis

- ✅ **Betano** - Funcional
- ✅ **Esportes da Sorte** - Funcional
- ⚠️ **Superbet** - Em desenvolvimento
- ⚠️ **Bet365** - Em desenvolvimento

---

## 📝 Exemplo de Saída

```
🏠 INICIANDO COLETA LOCAL (SEM PROXY)
================================================================================
📡 Enviando dados para: https://leite-bets-production.up.railway.app

📊 [1/4] BETANO
🇧🇷 Iniciando coleta BETANO (conexão local)
🏠 Iniciando browser LOCAL (sem proxy)
✅ Página carregada com sucesso
✅ Container de eventos encontrado
✅ Encontrados 8 jogos na Betano
✅ Betano: 8 jogos coletados e enviados

📊 [2/4] SUPERBET
⚠️ Parser da Superbet ainda não implementado

📊 [3/4] ESPORTES DA SORTE
🇧🇷 Iniciando coleta ESPORTES DA SORTE (conexão local)
✅ Encontrados 10 jogos
⚽ Processando: Flamengo vs Palmeiras
✅ Coletado: Flamengo vs Palmeiras - {'1X': 1.85, 'X2': 2.10, '12': 1.45}
...

================================================================================
🎯 RESUMO DA COLETA LOCAL
================================================================================
Total coletado: 13 jogos

✅ Enviado BETANO: 8 jogos
⚠️ SUPERBET: Sem dados
✅ Enviado ESPORTESDASORTE: 5 jogos
⚠️ BET365: Sem dados
```

---

## 🐛 Problemas Comuns

### ❌ "API_URL não configurada"
→ Configure `API_URL` no [.env.local](.env.local)

### ❌ "Timeout ao acessar site"
→ Sua internet pode estar lenta ou o site bloqueou seu IP

### ❌ "Falha no envio"
→ Verifique se a URL da API está correta e acessível

---

## 📚 Documentação Completa

Veja [scrapers/local/README.md](scrapers/local/README.md) para mais detalhes.

---

## 🔄 Próximos Passos

1. Teste rodando manualmente
2. Verifique se os dados chegam no banco do Railway
3. Configure automação (cron/Task Scheduler) se necessário
4. Monitore os logs para detectar problemas
