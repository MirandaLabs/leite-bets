# 🔧 IMPLEMENTAÇÃO - Código para Backend

> Código PRONTO para copiar/colar no `backend/main.py`

---

## 📍 LOCALIZAÇÃO

Adicione este código **DEPOIS dos imports** e **ANTES das rotas atuais** em `backend/main.py`.

---

## 📋 CHECKLIST PRÉ-IMPLEMENTAÇÃO

```
☐ Abri backend/main.py
☐ Verifiquei se FastAPI app já está criado
☐ Verifiquei se FastAPI tem imports necessários
☐ Tenho essas importações:
  ☐ from fastapi import FastAPI
  ☐ from datetime import datetime
  ☐ import logging
```

---

## 1️⃣ ADICIONAR IMPORTS (se não existirem)

No topo de `backend/main.py`, adicione:

```python
import os
import httpx
from fastapi import BackgroundTasks, HTTPException
import asyncio
import logging
```

---

## 2️⃣ CONFIGURAR LOGGING

Logo após o app = FastAPI(...), adicione:

```python
# Configure logging
logger = logging.getLogger(__name__)

# Configuração da URL do scraper
SCRAPER_API_URL = os.getenv("SCRAPER_API_URL", "http://localhost:8001")
SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "300"))  # 5 minutos
```

---

## 3️⃣ ADICIONAR OS 3 ENDPOINTS

### Endpoint 1: Trigger Todos os Scrapers

```python
@app.post("/api/trigger/all")
async def trigger_all_scrapers(background_tasks: BackgroundTasks):
    """
    Endpoint para disparar todos os scrapers.
    
    Executa em background (não bloqueia a requisição).
    
    Resposta:
    {
        "status": "triggered",
        "message": "Scrapers iniciados em background",
        "timestamp": "2026-01-28T15:30:45.123456"
    }
    
    Uso:
    curl -X POST https://seu-backend-railway.railway.app/api/trigger/all
    """
    background_tasks.add_task(run_all_scrapers_background)
    
    return {
        "status": "triggered",
        "message": "Scrapers iniciados em background",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Verifique os logs para acompanhar o progresso"
    }
```

### Endpoint 2: Trigger Scraper Específico

```python
@app.post("/api/trigger/{scraper_name}")
async def trigger_specific_scraper(
    scraper_name: str,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para disparar um scraper específico.
    
    Params:
    - scraper_name: betano, bet365, superbet, esportesdasorte
    
    Exemplo:
    POST /api/trigger/betano
    
    Resposta:
    {
        "status": "triggered",
        "scraper": "betano",
        "timestamp": "2026-01-28T15:30:45.123456"
    }
    """
    valid_scrapers = ["betano", "bet365", "superbet", "esportesdasorte"]
    
    if scraper_name.lower() not in valid_scrapers:
        raise HTTPException(
            status_code=400,
            detail=f"Scraper inválido. Use um de: {', '.join(valid_scrapers)}"
        )
    
    background_tasks.add_task(
        run_specific_scraper_background,
        scraper_name.lower()
    )
    
    return {
        "status": "triggered",
        "scraper": scraper_name,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Endpoint 3: Verificar Status

```python
@app.get("/api/scraper/status")
def get_scraper_status(db: Session = Depends(get_db)):
    """
    Retorna status do sistema de scraping.
    
    Resposta:
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
    
    Uso:
    curl https://seu-backend-railway.railway.app/api/scraper/status
    """
    try:
        total_events = db.query(Event).count()
        total_odds = db.query(Odd).count()
        upcoming_events = db.query(Event).filter(
            Event.status == "upcoming"
        ).count()
        live_events = db.query(Event).filter(
            Event.status == "live"
        ).count()
        finished_events = db.query(Event).filter(
            Event.status == "finished"
        ).count()
        
        # Encontra a última raspagem
        last_odd = db.query(Odd).order_by(Odd.scraped_at.desc()).first()
        last_scrape = last_odd.scraped_at if last_odd else None
        
        return {
            "status": "ok",
            "database": {
                "events": total_events,
                "odds": total_odds,
                "upcoming_events": upcoming_events,
                "live_events": live_events,
                "finished_events": finished_events
            },
            "last_scrape": last_scrape.isoformat() if last_scrape else None
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao verificar status")
```

---

## 4️⃣ ADICIONAR FUNÇÕES BACKGROUND

### Função 1: Executar Todos os Scrapers

```python
async def run_all_scrapers_background():
    """
    Executa todos os scrapers sequencialmente em background.
    """
    results = {}
    scrapers = ["betano", "bet365", "superbet", "esportesdasorte"]
    
    logger.info("🔄 Iniciando raspagem de TODOS os sites...")
    logger.info(f"URL do Scraper API: {SCRAPER_API_URL}")
    
    async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT) as client:
        for scraper in scrapers:
            try:
                logger.info(f"📊 Triggering {scraper}...")
                
                response = await client.post(
                    f"{SCRAPER_API_URL}/scrape/{scraper}",
                    timeout=SCRAPER_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items_count = len(data.get("data", []))
                    results[scraper] = {
                        "status": "success",
                        "items": items_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    logger.info(f"✅ {scraper}: {items_count} items coletados")
                else:
                    results[scraper] = {
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    logger.error(f"❌ {scraper}: HTTP {response.status_code}")
                    
            except httpx.TimeoutException:
                results[scraper] = {
                    "status": "error",
                    "error": "Timeout após 5 minutos",
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"❌ {scraper}: Timeout")
                
            except Exception as e:
                results[scraper] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"❌ {scraper}: {str(e)}")
    
    logger.info(f"✅ Raspagem completada. Resultados: {results}")
    return results
```

### Função 2: Executar Scraper Específico

```python
async def run_specific_scraper_background(scraper_name: str):
    """
    Executa um scraper específico em background.
    """
    logger.info(f"🔄 Iniciando raspagem: {scraper_name}")
    
    async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{SCRAPER_API_URL}/scrape/{scraper_name}",
                timeout=SCRAPER_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                items_count = len(data.get("data", []))
                logger.info(f"✅ {scraper_name}: {items_count} items coletados")
            else:
                logger.error(f"❌ {scraper_name}: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ {scraper_name}: {str(e)}")
```

---

## 5️⃣ VARIÁVEIS DE AMBIENTE

Adicione ao seu `.env` ou Railway Variables:

```env
# Configuração do Scraper
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300

# Logging
LOG_LEVEL=info
```

---

## 📋 RESUMO DO QUE FOI ADICIONADO

| Item | O quê |
|------|------|
| **Imports** | FastAPI, httpx, logging, etc |
| **Config** | SCRAPER_API_URL, SCRAPER_TIMEOUT |
| **Endpoints** | 3 novos endpoints (POST trigger/all, POST trigger/{nome}, GET status) |
| **Background Tasks** | 2 funções async para executar scrapers |
| **Logging** | Logs detalhados de cada passo |

---

## 🧪 TESTAR A IMPLEMENTAÇÃO

```bash
# 1. Reinicie o backend
python main.py

# 2. Teste o endpoint
curl -X POST http://localhost:8000/api/trigger/all

# 3. Verifique logs
# Deve mostrar:
# 🔄 Iniciando raspagem de TODOS os sites...
# 📊 Triggering betano...
# ... (conforme scrapers terminam)

# 4. Verifique status
curl http://localhost:8000/api/scraper/status

# 5. Verifique banco
# Dados devem aparecer após 2-3 minutos
```

---

## ✅ VERIFICAÇÃO FINAL

Depois de adicionar o código:

```
☐ Backend iniciou sem erros
☐ /health retorna status
☐ /api/trigger/all funciona
☐ /api/trigger/betano funciona
☐ /api/scraper/status funciona
☐ Logs mostram "✅" para cada scraper
☐ Dados aparecem no banco após 2-3 min
```

---

## 🎯 PRÓXIMO PASSO

Depois de implementar e testar:

1. Faça commit do código:
```bash
git add backend/main.py
git commit -m "feat: adicionar endpoints de trigger para scrapers"
git push
```

2. Configure no N8N (veja [RAILWAY_URLS_PRONTAS.md](RAILWAY_URLS_PRONTAS.md))

3. Ative o agendamento automático

---

## ❓ DÚVIDAS COMUNS

### "Posso modificar o código?"
Sim, personalize conforme necessário (timeouts, nomes dos scrapers, etc).

### "E se não tenho SCRAPER_API_URL?"
Deixe como `http://localhost:8001` para desenvolvimento local.

### "Como adiciono mais scrapers?"
Adicione na lista `scrapers = [...]` dentro de `run_all_scrapers_background()`.

### "E se quero rodar scrapers em paralelo?"
Modifique `run_all_scrapers_background()` para usar `asyncio.gather()` em vez de loop sequencial.

---

**Pronto para implementar!** ✨

Qualquer dúvida, consulte [EXEMPLO_TRIGGER_BACKEND.py](EXEMPLO_TRIGGER_BACKEND.py) para o código completo comentado.
