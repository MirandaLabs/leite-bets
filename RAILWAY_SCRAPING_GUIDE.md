# 🚀 Guia Definitivo - Executar Raspagem no Railway

## 📍 Visão Geral da Arquitetura

Seu projeto tem **2 APIs separadas**:

```
┌─────────────────────────────────────┐
│  BACKEND API (Railway)              │
│  Port 8000 - FastAPI                │
│  - Recebe odds do scraper           │
│  - Calcula arbitragem               │
│  - POST /api/odds/update            │
└─────────────────────────────────────┘
         ↑
         │ (dados)
         ↓
┌─────────────────────────────────────┐
│  SCRAPER API (Local/Docker)         │
│  Port 8001 - FastAPI                │
│  - Coleta dados dos sites           │
│  - POST /scrape/betano              │
│  - POST /scrape/bet365              │
│  - POST /scrape/superbet            │
│  - POST /scrape/esportesdasorte     │
└─────────────────────────────────────┘
```

---

## ✅ OPÇÃO 1: Trigger via N8N (RECOMENDADO)

A forma **mais segura** e **melhor para produção** no Railway.

### ⚙️ Setup

1. **Adicione um novo endpoint no Backend** (`backend/main.py`):

```python
from fastapi import BackgroundTasks
from datetime import datetime
import httpx
import asyncio

# Configuração - adicione ao topo do arquivo
SCRAPER_API_URL = os.getenv("SCRAPER_API_URL", "http://localhost:8001")

@app.post("/api/trigger/all")
async def trigger_all_scrapers(background_tasks: BackgroundTasks):
    """
    Trigger para todos os scrapers (chamado pelo N8N)
    """
    background_tasks.add_task(run_all_scrapers)
    
    return {
        "status": "triggered",
        "message": "Scrapers iniciados em background",
        "timestamp": datetime.utcnow().isoformat()
    }

async def run_all_scrapers():
    """Executa todos os scrapers sequencialmente"""
    results = {}
    
    scrapers = ["betano", "bet365", "superbet", "esportesdasorte"]
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        for scraper in scrapers:
            try:
                print(f"🔄 Triggering {scraper}...")
                response = await client.post(
                    f"{SCRAPER_API_URL}/scrape/{scraper}"
                )
                results[scraper] = {
                    "status": "success" if response.status_code == 200 else "error",
                    "items": len(response.json().get("data", []))
                }
                print(f"✅ {scraper} completed: {results[scraper]}")
            except Exception as e:
                print(f"❌ {scraper} failed: {str(e)}")
                results[scraper] = {"status": "error", "error": str(e)}
    
    return results
```

2. **Configure variável no Railway**:

```env
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
```

3. **Configure no N8N**:

```
Schedule Trigger (a cada 30 min)
    ↓
HTTP Request (POST)
    ↓
URL: https://seu-backend-railway.railway.app/api/trigger/all
Method: POST
Headers: Content-Type: application/json
```

### ✅ Vantagens
- ✅ Não bloqueia requisição (background tasks)
- ✅ Melhor tratamento de erros
- ✅ Logs centralizados
- ✅ Escala bem em produção
- ✅ Pode ser agendado

---

## 🔄 OPÇÃO 2: Trigger Direto do N8N para Scraper

Se você quer **executar o scraper diretamente** (mais rápido, menos seguro).

### ⚙️ Setup

**No N8N, use este endpoint:**

```
POST https://seu-scraper-railway.railway.app/scrape/betano
POST https://seu-scraper-railway.railway.app/scrape/bet365
POST https://seu-scraper-railway.railway.app/scrape/superbet
POST https://seu-scraper-railway.railway.app/scrape/esportesdasorte
```

### Workflow N8N:
```
Schedule Trigger
    ↓
HTTP Request → /scrape/betano
    ↓
IF (status === 200)
    ↓
Parse JSON
    ↓
Loop through items
    ↓
HTTP Request → Backend /api/odds/update
```

### ⚠️ Desvantagens
- ❌ Timeout após 30s (requisições podem falhar)
- ❌ Precisa de retry logic mais complexa
- ❌ Mais difícil de debugar

---

## 🎯 OPÇÃO 3: Trigger Manual via cURL (Testes)

Para **testar rapidamente** ou **debug**:

```bash
# Trigger todos os scrapers via Backend
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Trigger scraper específico direto
curl -X POST https://seu-scraper-railway.railway.app/scrape/betano

# Verificar status do backend
curl https://seu-backend-railway.railway.app/health

# Verificar status do scraper
curl https://seu-scraper-railway.railway.app/health
```

---

## 📋 Checklist para Railway

### Backend Service

```env
DATABASE_URL=postgresql://user:pass@host:port/db
TELEGRAM_BOT_TOKEN=seu_token
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
```

**Entrypoint:**
```bash
sh ./backend/entrypoint-railway.sh
```

### Scraper Service

```env
# Variáveis do proxy (opcional)
IP_1=xxx
IP_2=xxx
# ... até IP_10

# Para logging
LOG_LEVEL=info
```

**Entrypoint:**
```bash
python -m scrapers.api.main
```

Ou via uvicorn:
```bash
uvicorn scrapers.api.main:app --host 0.0.0.0 --port 8000
```

---

## 🔗 Fluxo Completo no Railway

```
┌─────────────┐
│   N8N       │ (Cron job a cada 30min)
└──────┬──────┘
       │
       └──→ POST /api/trigger/all
            │
       ┌────▼─────────────────────────┐
       │   Backend (Railway)           │
       │   ├─ DB: PostgreSQL           │
       │   ├─ Bot: Telegram            │
       │   └─ Port: 8000               │
       └────┬─────────────────────────┘
            │
            │ (faz request para)
            │
       ┌────▼─────────────────────────┐
       │   Scraper (Railway)           │
       │   ├─ Betano                   │
       │   ├─ Bet365                   │
       │   ├─ Superbet                 │
       │   └─ EsportesDaSorte          │
       │   └─ Port: 8000               │
       └────┬─────────────────────────┘
            │
            │ (retorna dados para)
            │
       ┌────▼─────────────────────────┐
       │   Backend armazena no DB      │
       │   e notifica Telegram         │
       └──────────────────────────────┘
```

---

## 🧪 Testar Localmente Primeiro

### 1. Com Docker Compose

```bash
# Terminal 1: Inicia todos os serviços
docker-compose up

# Terminal 2: Trigger manualmente
curl -X POST http://localhost:8000/api/trigger/all
```

### 2. Verificar logs

```bash
# Logs do scraper
docker-compose logs -f scraper

# Logs do backend
docker-compose logs -f api

# Logs do banco
docker-compose logs -f postgres
```

### 3. Testar scraper diretamente

```bash
# Acessa scraper direto
curl -X POST http://localhost:8001/scrape/betano

# Resposta esperada:
{
  "source": "betano",
  "items": 25,
  "data": [...]
}
```

---

## ⚠️ Pontos Críticos para Produção

### 1. **Timeout das Requisições**
- Scrapers podem levar **60-120 segundos**
- Configure timeout de pelo menos **300 segundos** no N8N
- Use **background tasks** para não bloquear a API

### 2. **Rate Limiting**
- Sites podem bloquear por muitas requisições
- Use proxies (já configurado com 10 IPs)
- Implemente delay entre scrapers

### 3. **Monitoramento**
- Verifique logs regularmente no Railway
- Configure alertas para falhas de scraper
- Monitore uso de banda e CPU

### 4. **Dados Duplicados**
- Implemente dedup por `(event_id, bookmaker, timestamp)`
- Atualize em vez de inserir registros duplicados

### 5. **Limpeza de Dados**
```bash
# Remover eventos com mais de 7 dias
curl -X DELETE http://seu-backend/api/events/cleanup?days_old=7
```

---

## 📊 Variáveis de Ambiente Recomendadas

Para Railway, adicione essas variáveis:

```env
# Database
DATABASE_URL=postgresql://...

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Scraper
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300

# Proxies
IP_1=...
IP_2=...
# ... até IP_10

# Logging
LOG_LEVEL=info
```

---

## 🚀 Deploy Rápido

### 1. Crie dois serviços no Railway

```bash
# Railway CLI
railway service create backend
railway service create scraper
railway service create postgres
```

### 2. Aponte para os Dockerfiles

```
Backend → ./backend/Dockerfile
Scraper → ./scrapers/dockerfile
Postgres → image: postgres:16-alpine
```

### 3. Configure variáveis

```
Backend: DATABASE_URL, TELEGRAM_BOT_TOKEN, SCRAPER_API_URL
Scraper: SCRAPER_TIMEOUT, IP_1...IP_10
Postgres: POSTGRES_PASSWORD, POSTGRES_DB
```

### 4. Configure N8N para chamar Backend

```
POST https://seu-backend-railway.railway.app/api/trigger/all
```

**Pronto! 🎉**

---

## 📞 Troubleshooting

| Problema | Solução |
|----------|---------|
| Timeout após 30s | Aumentar timeout no N8N, usar background tasks |
| Scraper retorna erro 500 | Verificar logs: `railway logs --service scraper` |
| Dados não salvam no DB | Verificar DATABASE_URL e credenciais |
| Bot não envia notificação | Verificar TELEGRAM_BOT_TOKEN e CHAT_ID |
| Proxy bloqueando | Trocar IP ou desativar proxy (comentar em proxy_manager.py) |

---

## 🎯 Resumo das 3 Opções

| Opção | Melhor Para | Complexidade | Reliability |
|-------|-------------|--------------|-------------|
| **1. N8N → Backend → Scraper** | Produção | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **2. N8N → Scraper direto** | Testes | ⭐⭐ | ⭐⭐ |
| **3. cURL manual** | Debug | ⭐ | ⭐ |

**Recomendação: Use a OPÇÃO 1 para Railway!** ✅
