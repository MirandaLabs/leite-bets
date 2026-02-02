# 🔗 Guia de Integração N8N - LeiteBets

## 🎯 Endpoints disponíveis

### 1. Trigger TODOS os scrapers
```
POST https://sua-url.ngrok.io/api/trigger/all
```

**Resposta:**
```json
{
  "triggered_at": "2026-01-28T...",
  "scrapers": {
    "betano": {"status": "success", "items": 15},
    "bet365": {"status": "success", "items": 12},
    ...
  }
}
```

---

### 2. Trigger scraper específico
```
POST https://sua-url.ngrok.io/api/trigger/{casa}
```

Casas disponíveis: `betano`, `bet365`, `superbet`, `esportesdasorte`

**Exemplo:**
```
POST https://sua-url.ngrok.io/api/trigger/betano
```

---

### 3. Verificar status
```
GET https://sua-url.ngrok.io/api/scraper/status
```

**Resposta:**
```json
{
  "status": "ok",
  "database": {
    "events": 25,
    "odds": 100,
    "upcoming_events": 20
  }
}
```

---

### 4. Webhook genérico
```
POST https://sua-url.ngrok.io/api/webhook/n8n
```

**Body (JSON):**
```json
{
  "action": "scrape_all"
}
```

**Ações disponíveis:**
- `"scrape_all"` - Triggera todos
- `"scrape_casa"` + `"casa": "betano"` - Triggera específico
- `"status"` - Retorna status

---

## 🔄 Setup no N8N

### Workflow recomendado:
```
Schedule Trigger (a cada 30 min)
    ↓
HTTP Request (POST /api/trigger/all)
    ↓
IF (status === "success")
    ↓
Slack/Email (Notificação de sucesso)
```

### Configuração do HTTP Request Node:

**Method:** POST  
**URL:** `https://sua-url.ngrok.io/api/trigger/all`  
**Authentication:** None  
**Headers:**
```
Content-Type: application/json
```

---

## ⏰ Intervalo recomendado

- **30 minutos** - Para odds em tempo real
- **60 minutos** - Para economia de recursos
- **15 minutos** - Para alta frequência (jogos ao vivo)

---

## 🧪 Testar endpoints

**cURL:**
```bash
# Trigger todos
curl -X POST https://sua-url.ngrok.io/api/trigger/all

# Status
curl https://sua-url.ngrok.io/api/scraper/status

# Webhook
curl -X POST https://sua-url.ngrok.io/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{"action":"scrape_all"}'
```

---

## ✅ Checklist

- [ ] Ngrok rodando (ou deploy feito)
- [ ] Endpoint `/api/trigger/all` testado
- [ ] N8N configurado com Schedule Trigger
- [ ] HTTP Request apontando para endpoint correto
- [ ] Workflow ativado
- [ ] Bot do Telegram rodando

**Pronto! Automação completa!** 🚀
```

**Salve!**

---

## 🎯 RESUMO PRO SÓCIO:

**Manda isso pra ele:**
```
Endpoints prontos pro N8N:

1. TRIGGER TUDO:
POST https://marian-precocious-defyingly.ngrok-free.dev/api/trigger/all

2. VERIFICAR STATUS:
GET https://marian-precocious-defyingly.ngrok-free.dev/api/scraper/status

3. WEBHOOK GENÉRICO:
POST https://marian-precocious-defyingly.ngrok-free.dev/api/webhook/n8n
Body: {"action": "scrape_all"}

No N8N é só criar:
- Schedule Trigger (30 min)
- HTTP Request (POST pro endpoint 1)
- Pronto! ✅