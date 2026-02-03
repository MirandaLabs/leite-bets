# ✅ Validação e Teste - Scraping no Railway

> Guia passo a passo para validar que tudo está funcionando corretamente

---

## 🔍 PASSO 1: Verificar Serviços no Railway

### Terminal

```bash
# Listar todos os serviços
railway service list

# Saída esperada:
# NAME      STATUS
# backend   active
# scraper   active
# postgres  active
```

### Dashboard Railway

1. Acesse https://railway.app
2. Selecione seu projeto
3. Verifique se os 3 serviços têm status verde ✅

---

## 🧪 PASSO 2: Health Checks Básicos

### 2.1 Backend está online?

```bash
curl https://seu-backend-railway.railway.app/health
```

**Resposta esperada:**
```json
{
  "status": "healthy"
}
```

❌ Se falhar: Backend não está respondendo, verifique logs
```bash
railway logs --service backend --follow
```

### 2.2 Scraper está online?

```bash
curl https://seu-scraper-railway.railway.app/health
```

**Resposta esperada:**
```json
{
  "status": "ok"
}
```

❌ Se falhar: Scraper não está respondendo, verifique logs
```bash
railway logs --service scraper --follow
```

### 2.3 Banco de dados está acessível?

```bash
curl https://seu-backend-railway.railway.app/api/scraper/status
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "database": {
    "events": 0,
    "odds": 0,
    "upcoming_events": 0,
    "live_events": 0,
    "finished_events": 0
  },
  "last_scrape": null
}
```

❌ Se falhar com erro de database: DATABASE_URL incorreto
```bash
railway env --service backend
# Verifique: DATABASE_URL está correto?
```

---

## 🔌 PASSO 3: Testar Conexão Backend → Scraper

O backend precisa conseguir chamar o scraper.

### 3.1 Verifique SCRAPER_API_URL

```bash
# Ver configuração
railway env --service backend | grep SCRAPER_API_URL

# Resposta esperada:
# SCRAPER_API_URL=https://seu-scraper-railway.railway.app
```

### 3.2 Teste direto da requisição

```bash
# Do seu PC, faça com um delay
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Aguarde 2-3 segundos
sleep 3

# Verifique logs do backend
railway logs --service backend --tail 50

# Você deve ver:
# 🔄 Iniciando raspagem de TODOS os sites...
# 📊 Triggering betano...
```

---

## 🕸️ PASSO 4: Testar Scraper Direto

Para isolar se o problema está no scraper ou na conexão.

### 4.1 Chamar scraper diretamente

```bash
curl -X POST https://seu-scraper-railway.railway.app/scrape/betano

# Resposta esperada (pode demorar 20-40 segundos):
{
  "source": "betano",
  "items": 25,
  "data": [
    {
      "id": "event_123",
      "name": "Time A vs Time B",
      "start_time": "2026-01-28T20:00:00Z",
      "odds": [
        {
          "bookmaker": "betano",
          "home": 2.10,
          "draw": 3.20,
          "away": 3.50
        }
      ]
    },
    ...
  ]
}
```

❌ Se timeout: aumentar timeout do curl
```bash
curl --max-time 120 -X POST https://seu-scraper-railway.railway.app/scrape/betano
```

---

## 📊 PASSO 5: Testar Salvamento no Banco

Após triggar os scrapers, dados devem ser salvos.

### 5.1 Trigger e aguarde

```bash
# Trigger
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Aguarde 3-5 minutos (scrapers rodam em background)
echo "Aguardando scrapers... (3-5 min)"
sleep 180

# Verifique status
curl https://seu-backend-railway.railway.app/api/scraper/status
```

**Resposta esperada após 5 minutos:**
```json
{
  "status": "ok",
  "database": {
    "events": 95,
    "odds": 380,
    "upcoming_events": 85,
    "live_events": 3,
    "finished_events": 7
  },
  "last_scrape": "2026-01-28T15:32:36Z"
}
```

❌ Se não aumentar: dados não estão sendo salvos
- Verifique logs do backend: `railway logs --service backend | grep "ERROR"`
- Verifique logs do scraper: `railway logs --service scraper | grep "ERROR"`

---

## 🤖 PASSO 6: Testar N8N Integration

### 6.1 Abra N8N

- Se local: http://localhost:5678
- Se Railway: Verifique a URL no dashboard

### 6.2 Crie um workflow de teste

**Nodes:**

1. **Manual Trigger** (ou Schedule)
2. **HTTP Request**
   - Method: POST
   - URL: `https://seu-backend-railway.railway.app/api/trigger/all`
3. **Execute**

### 6.3 Execute manualmente

Clique em "Execute Workflow" no N8N e verifique:
- ✅ HTTP Request retorna status 200
- ✅ Response contém `"status": "triggered"`

---

## 🧠 PASSO 7: Teste Completo (End-to-End)

### Cronograma:

```
T+0s:   Trigger via N8N ou curl
T+1s:   Backend retorna "triggered"
T+2s:   Backend começa a chamar scrapers em background
T+60s:  Scrapers terminam de coletar dados
T+65s:  Dados são salvos no banco
T+66s:  Bot do Telegram envia notificação
```

### Verificação:

```bash
# T+0: Trigger
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# T+10: Verifique logs
railway logs --service backend --tail 30
# Deve mostrar: "🔄 Iniciando raspagem..."

# T+70: Verifique dados
curl https://seu-backend-railway.railway.app/api/scraper/status
# Campo "last_scrape" deve estar atualizado

# T+75: Verifique Telegram
# Deve ter recebido notificação do bot
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

```
INFRAESTRUTURA:
- [ ] Backend status: ✅
- [ ] Scraper status: ✅
- [ ] Postgres acessível: ✅
- [ ] DATABASE_URL configurado: ✅
- [ ] SCRAPER_API_URL configurado: ✅

CONECTIVIDADE:
- [ ] /health do backend: ✅
- [ ] /health do scraper: ✅
- [ ] Backend consegue chamar scraper: ✅
- [ ] Scraper consegue fazer requests: ✅

FUNCIONALIDADE:
- [ ] /api/trigger/all retorna "triggered": ✅
- [ ] /api/trigger/{scraper} funciona: ✅
- [ ] /api/scraper/status retorna dados: ✅
- [ ] Dados salvam no banco: ✅
- [ ] Telegram recebe notificações: ✅

N8N:
- [ ] HTTP Request conecta ao backend: ✅
- [ ] Schedule Trigger funciona: ✅
- [ ] Workflow executa sem erros: ✅

LOGS:
- [ ] Backend logs limpos (sem ERROR): ✅
- [ ] Scraper logs limpos (sem ERROR): ✅
- [ ] Postgres conectando normalmente: ✅
```

---

## 🔴 ERROS COMUNS E SOLUÇÕES

### Erro: "Connection refused"

```bash
# Problema: Scraper não está respondendo
# Solução 1: Verifique se está ativo
railway service list

# Solução 2: Verifique logs
railway logs --service scraper --follow

# Solução 3: Reinicie
railway service restart scraper
```

### Erro: "Timeout"

```bash
# Problema: Requisição leva mais tempo que timeout padrão
# Solução: Aumente timeout no N8N (30s) ou nos headers:

curl --max-time 120 -X POST https://seu-backend-railway.railway.app/api/trigger/all

# No N8N, configure timeout no HTTP Request node para 120 segundos
```

### Erro: "Database connection error"

```bash
# Problema: Postgres não acessível
# Solução 1: Verifique DATABASE_URL
railway env --service backend | grep DATABASE_URL

# Solução 2: Teste conexão manualmente
psql "$DATABASE_URL" -c "SELECT 1"

# Solução 3: Verifique credenciais
# Postgres deve ter POSTGRES_PASSWORD configurado
railway env --service postgres
```

### Erro: "No items returned"

```bash
# Problema: Scraper retorna array vazio
# Pode ser seletores quebrados ou site bloqueou

# Solução 1: Verifique logs do scraper
railway logs --service scraper | grep "betano\|ERROR"

# Solução 2: Teste com debug endpoint
curl https://seu-scraper-railway.railway.app/debug/betano-html

# Solução 3: Verifique proxies (se usando)
railway env --service scraper | grep "^IP_"
```

---

## 📈 PERFORMANCE

Tempos esperados (com proxies, 4 scrapers):

| Etapa | Tempo |
|-------|-------|
| Trigger API | <1s |
| Backend em background | ~0-2s |
| Scraper Betano | 20-40s |
| Scraper Bet365 | 15-30s |
| Scraper Superbet | 20-35s |
| Scraper EsportesDaSorte | 20-40s |
| **Total** | **60-120s** |

---

## 🎯 FLUXO DE DEBUG

Se algo não funciona, siga esta ordem:

```
1. ✅ Health Check Backend
   ↓ Se falha → Verifique deploy
   
2. ✅ Health Check Scraper
   ↓ Se falha → Verifique deploy
   
3. ✅ Status do Banco
   ↓ Se falha → Verifique DATABASE_URL
   
4. ✅ Chame /api/trigger/all
   ↓ Se falha → Verifique logs do backend
   
5. ✅ Aguarde 2-3 min e verifique status
   ↓ Se dados não aumentam → Verifique logs do scraper
   
6. ✅ Verifique logs do Telegram
   ↓ Se não receber → Verifique TELEGRAM_BOT_TOKEN
   
7. ✅ Teste N8N manualmente
   ↓ Se falha → Configure URL correta no HTTP Request node
   
8. ✅ Configure Schedule Trigger
   ↓ Pronto! ✨
```

---

## 📊 MONITORAMENTO CONTÍNUO

Depois de tudo validado, monitore com:

```bash
# Terminal 1: Logs do backend
railway logs --service backend --follow

# Terminal 2: Logs do scraper  
railway logs --service scraper --follow

# Terminal 3: Checar status periodicamente
watch -n 300 'curl https://seu-backend-railway.railway.app/api/scraper/status'
```

---

## ✅ PRONTO!

Se passou em todos os checklists, sua infraestrutura está **100% operacional**! 🚀

Qualquer dúvida, consulte:
- [RAILWAY_SCRAPING_GUIDE.md](RAILWAY_SCRAPING_GUIDE.md) - Guia completo
- [RAILWAY_URLS_PRONTAS.md](RAILWAY_URLS_PRONTAS.md) - Endpoints e URLs
- [EXEMPLO_TRIGGER_BACKEND.py](EXEMPLO_TRIGGER_BACKEND.py) - Código exemplo
