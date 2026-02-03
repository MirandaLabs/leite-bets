# 🚀 DISPARAR SCRAPERS VIA CURL

## 📍 ENDPOINTS DISPONÍVEIS

### 1. Disparar TODOS os scrapers (Recomendado)

```powershell
# PowerShell (Windows)
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/all

# Ou com Invoke-WebRequest (mais detalhado)
Invoke-WebRequest -Uri "https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/all" -Method POST

# Bash/Linux/Mac
curl -X POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/all
```

**Resposta esperada:**
```json
{
  "status": "triggered",
  "message": "Scrapers iniciados em background",
  "timestamp": "2026-02-03T16:15:00.123456",
  "note": "Verifique os logs para acompanhar o progresso"
}
```

---

### 2. Disparar scraper específico

```powershell
# Betano
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/betano

# Bet365
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/bet365

# Superbet
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/superbet

# EsportesDaSorte
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/esportesdasorte
```

---

### 3. Verificar status

```powershell
# Ver quantos eventos/odds foram coletados
curl https://SEU-BACKEND-RAILWAY.railway.app/api/scraper/status
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
  "last_scrape": "2026-02-03T16:10:00Z"
}
```

---

## 🔍 ENCONTRAR A URL DO BACKEND

### Opção 1: Railway Dashboard

1. Acesse https://railway.app
2. Selecione seu projeto
3. Clique no serviço **Backend** ou **API**
4. Veja a URL em **Settings → Networking**

### Opção 2: Variáveis de Ambiente

Se você configurou `SCRAPER_API_URL` no serviço bot, o backend deve ter uma URL similar.

### Opção 3: Listar serviços

```powershell
# Se tiver Railway CLI instalado
railway service list
```

---

## 📊 FLUXO COMPLETO DE TESTE

```powershell
# 1. Health check do bot (já funcionou! ✅)
curl https://service-bot-production-990d.up.railway.app/health

# 2. Health check do backend
curl https://SEU-BACKEND-RAILWAY.railway.app/health

# 3. Disparar todos os scrapers
curl -Method POST https://SEU-BACKEND-RAILWAY.railway.app/api/trigger/all

# 4. Aguardar 2-3 minutos (scrapers rodando)
Start-Sleep -Seconds 180

# 5. Verificar status
curl https://SEU-BACKEND-RAILWAY.railway.app/api/scraper/status

# 6. Verificar Telegram
# Você deve receber notificação com os dados coletados
```

---

## ⚠️ SE O BACKEND NÃO ESTIVER DEPLOYADO

Se você ainda não deployou o backend no Railway, precisa:

1. **Criar serviço Backend no Railway**
   ```
   - Dockerfile: backend/Dockerfile
   - Watch Path: backend/**
   ```

2. **Adicionar variáveis de ambiente:**
   ```env
   DATABASE_URL=postgresql://...
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   SCRAPER_API_URL=https://seu-scraper-railway.railway.app
   ```

3. **Deploy e aguardar**

4. **Testar health check:**
   ```powershell
   curl https://seu-backend-railway.railway.app/health
   ```

---

## 🎯 EXEMPLO COMPLETO (substitua a URL)

```powershell
# Defina a URL do backend
$BACKEND_URL = "https://seu-backend-railway.railway.app"

# 1. Teste health check
Write-Host "🏥 Testando health check..." -ForegroundColor Cyan
curl "$BACKEND_URL/health"

# 2. Disparar scrapers
Write-Host "`n🚀 Disparando scrapers..." -ForegroundColor Green
curl -Method POST "$BACKEND_URL/api/trigger/all"

# 3. Aguardar
Write-Host "`n⏳ Aguardando scrapers (3 minutos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 180

# 4. Verificar resultado
Write-Host "`n📊 Verificando resultados..." -ForegroundColor Cyan
curl "$BACKEND_URL/api/scraper/status"

Write-Host "`n✅ Concluído! Verifique o Telegram para notificações." -ForegroundColor Green
```

---

## 📞 PRÓXIMOS PASSOS

1. **Encontre a URL do seu backend no Railway**
2. **Substitua `SEU-BACKEND-RAILWAY.railway.app` nos comandos acima**
3. **Execute o teste completo**
4. **Verifique os resultados**

---

**Me informe a URL do backend quando encontrar, e eu ajusto os comandos!** 🎯
