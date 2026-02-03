# 🎯 URLs e Comandos Prontos - Railway

> **Última atualização:** Fevereiro 2026
> **Status:** Production Ready

---

## 📍 ENDPOINTS PRONTOS PARA USAR

### 1️⃣ TRIGGER TODOS OS SCRAPERS (Recomendado)

```bash
# Trigger via Backend (aguarda no máximo 10s de resposta)
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Com timeout customizado
curl -X POST --max-time 30 https://seu-backend-railway.railway.app/api/trigger/all
```

**Resposta esperada:**
```json
{
  "status": "triggered",
  "message": "Scrapers iniciados em background",
  "timestamp": "2026-01-28T15:30:45.123456",
  "note": "Verifique os logs para acompanhar o progresso"
}
```

**O que acontece:**
- ✅ Requisição retorna em menos de 1 segundo
- ✅ Scrapers rodam em background (60-120 segundos)
- ✅ Dados são salvos automaticamente no banco
- ✅ Bot do Telegram recebe notificações

---

### 2️⃣ TRIGGER SCRAPER ESPECÍFICO

```bash
# Betano
curl -X POST https://seu-backend-railway.railway.app/api/trigger/betano

# Bet365
curl -X POST https://seu-backend-railway.railway.app/api/trigger/bet365

# Superbet
curl -X POST https://seu-backend-railway.railway.app/api/trigger/superbet

# EsportesDaSorte
curl -X POST https://seu-backend-railway.railway.app/api/trigger/esportesdasorte
```

---

### 3️⃣ VERIFICAR STATUS DO SISTEMA

```bash
# Status geral (eventos, odds, última raspagem)
curl https://seu-backend-railway.railway.app/api/scraper/status
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "database": {
    "events": 150,
    "odds": 450,
    "upcoming_events": 120,
    "live_events": 5,
    "finished_events": 25
  },
  "last_scrape": "2026-01-28T15:30:00Z"
}
```

---

### 4️⃣ HEALTH CHECKS

```bash
# Backend
curl https://seu-backend-railway.railway.app/health

# Scraper
curl https://seu-scraper-railway.railway.app/health
```

**Resposta:**
```json
{
  "status": "healthy"
}
```

---

## 🔧 CONFIGURAÇÃO NO N8N

### Workflow Recomendado

```
┌─────────────────────────┐
│  Schedule Trigger       │
│  (a cada 30 min)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  HTTP Request           │
│  POST /api/trigger/all  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  IF success             │
│  status === "triggered" │
└────────┬────────────────┘
         │
         ├──▶ Telegram Notification
         │    "Raspagem iniciada"
         │
         └──▶ Wait 2 min
              │
              ▼
              GET /api/scraper/status
              │
              └──▶ Telegram
                   "Dados: X eventos, Y odds"
```

### Node de HTTP Request

**Configuração:**

| Campo | Valor |
|-------|-------|
| **Method** | POST |
| **URL** | `https://seu-backend-railway.railway.app/api/trigger/all` |
| **Content Type** | JSON |
| **Headers** | `Content-Type: application/json` |
| **Timeout** | 30 segundos |
| **Retry** | 3 vezes com delay de 30s |

**JSON Body (deixe vazio):**
```json
{}
```

### Node de Wait

```
Wait: 120 segundos
(scrapers rodam neste tempo)
```

### Node de GET Status

**Configuração:**

| Campo | Valor |
|-------|-------|
| **Method** | GET |
| **URL** | `https://seu-backend-railway.railway.app/api/scraper/status` |

---

## 🕐 AGENDAMENTO RECOMENDADO

| Frequência | Caso de Uso | Configuração N8N |
|-----------|-----------|------------------|
| **A cada 15 min** | Jogos ao vivo | Cron: `*/15 * * * *` |
| **A cada 30 min** | Odds em tempo real (padrão) | Cron: `*/30 * * * *` |
| **A cada 60 min** | Economia de banda | Cron: `0 * * * *` |
| **2x por dia** | Apenas manhã/noite | Cron: `0 8,20 * * *` |

**Exemplo N8N Schedule Trigger:**
```
Cron: 0 */6 * * *  (a cada 6 horas)
```

---

## 📊 MONITORAMENTO

### Logs do Backend no Railway

```bash
# Ver logs em tempo real
railway logs --service backend --follow

# Procurar por erros
railway logs --service backend | grep "❌"

# Procurar por sucessos
railway logs --service backend | grep "✅"
```

### Exemplo de log esperado:

```
2026-01-28T15:30:45 🔄 Iniciando raspagem de TODOS os sites...
2026-01-28T15:30:46 📊 Triggering betano...
2026-01-28T15:31:05 ✅ betano: 25 items coletados
2026-01-28T15:31:06 📊 Triggering bet365...
2026-01-28T15:31:45 ✅ bet365: 18 items coletados
2026-01-28T15:31:46 📊 Triggering superbet...
2026-01-28T15:32:10 ✅ superbet: 31 items coletados
2026-01-28T15:32:11 📊 Triggering esportesdasorte...
2026-01-28T15:32:35 ✅ esportesdasorte: 22 items coletados
2026-01-28T15:32:36 ✅ Raspagem completada
```

---

## ⚙️ VARIÁVEIS DE AMBIENTE NO RAILWAY

Adicione estas variáveis no **Backend Service**:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Scraper (IMPORTANTE!)
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300

# Logging
LOG_LEVEL=info

# Proxies (opcional)
IP_1=xxx.xxx.xxx.xxx
IP_2=xxx.xxx.xxx.xxx
# ... até IP_10
```

---

## 🚨 TROUBLESHOOTING

### ❌ Erro: "Connection refused" ao chamar scraper

**Causa:** Scraper API não está acessível  
**Solução:**

```bash
# 1. Verifique se scraper está rodando
curl https://seu-scraper-railway.railway.app/health

# 2. Verifique SCRAPER_API_URL no backend
railway env --service backend

# 3. Se local, use http://scraper:8000 (docker-compose)
# Se Railway, use https://seu-scraper-railway.railway.app
```

### ❌ Erro: "Timeout após 300 segundos"

**Causa:** Scraper levou mais tempo que esperado  
**Solução:**

```bash
# 1. Aumente SCRAPER_TIMEOUT no backend
railway env --update SCRAPER_TIMEOUT=600

# 2. Verifique logs do scraper
railway logs --service scraper --follow

# 3. Considere paralelizar scrapers (mais complexo)
```

### ❌ Erro: "HTTP 400 - Scraper inválido"

**Causa:** Nome do scraper escrito errado  
**Solução:**

```bash
# Use um destes nomes:
# - betano
# - bet365
# - superbet
# - esportesdasorte

curl -X POST https://seu-backend-railway.railway.app/api/trigger/betano
```

### ✅ Tudo funciona, mas dados não aparecem no banco

**Causa:** DATABASE_URL incorrea ou sem conexão  
**Solução:**

```bash
# 1. Teste a conexão
psql "$DATABASE_URL"

# 2. Verifique status
curl https://seu-backend-railway.railway.app/api/scraper/status

# 3. Verifique logs
railway logs --service backend | grep "ERROR"
```

---

## 📋 CHECKLIST PRÉ-DEPLOY

- [ ] Backend rodando no Railway com DATABASE_URL
- [ ] Scraper rodando no Railway separado
- [ ] SCRAPER_API_URL configurado no Backend
- [ ] N8N integrado e testado
- [ ] Telegram Bot TOKEN e CHAT_ID configurados
- [ ] Proxies configurados (se usando)
- [ ] Testado localmente com docker-compose
- [ ] Logado em Railway e verificado os serviços
- [ ] Endpoints testados com curl
- [ ] Workflow N8N ativado
- [ ] Alertas configurados (Telegram, email, etc)

---

## 🎯 RESUMO RÁPIDO

**Para executar raspagem no Railway:**

1. **Trigger Manual (testes):**
   ```bash
   curl -X POST https://seu-backend-railway.railway.app/api/trigger/all
   ```

2. **Automático (produção):**
   - Configure N8N com Schedule Trigger
   - Aponte para: `POST /api/trigger/all`
   - Intervalo: 30 minutos

3. **Monitorar:**
   ```bash
   curl https://seu-backend-railway.railway.app/api/scraper/status
   ```

**Pronto!** ✅

---

## 📞 SUPORTE

- **Logs:** `railway logs --service [backend|scraper]`
- **Env Vars:** `railway env`
- **Documentação Completa:** Veja `RAILWAY_SCRAPING_GUIDE.md`
