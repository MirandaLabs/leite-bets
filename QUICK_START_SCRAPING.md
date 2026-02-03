# 🎯 GUIA RÁPIDO - Executar Scrapers no Railway

> **TL;DR** - Versão super resumida (2 minutos)

---

## ❓ PERGUNTA

> Baseando-se na configuração atual do projeto e seu deploy no Railway, qual a melhor forma de executar a requisição que inicia a raspagem dos sites?

## ✅ RESPOSTA RÁPIDA

**Use N8N com Schedule Trigger a cada 30 minutos** que faz POST para `/api/trigger/all`

```
N8N (timer) → POST /api/trigger/all → Backend → Scrapers → DB → Telegram
      30 min      (instantâneo)        (2-3 min)   (60-120s)  (auto) (notifica)
```

---

## 🚀 3 OPÇÕES

| # | Opção | Melhor Para | Setup | Como |
|---|-------|-------------|-------|------|
| ✅ | **N8N Automático** | Produção | 15 min | Schedule → POST /api/trigger/all |
| 🧪 | N8N Manual | Testes | 5 min | Execute manualmente no N8N |
| 🐚 | cURL Manual | Debug | 0 min | `curl -X POST .../api/trigger/all` |

**Recomendação: Use OPÇÃO 1** ✅

---

## 📍 ENDPOINTS PRONTOS

```bash
# Disparar tudo
POST https://seu-backend-railway.railway.app/api/trigger/all

# Disparar específico
POST https://seu-backend-railway.railway.app/api/trigger/betano
POST https://seu-backend-railway.railway.app/api/trigger/bet365
POST https://seu-backend-railway.railway.app/api/trigger/superbet
POST https://seu-backend-railway.railway.app/api/trigger/esportesdasorte

# Verificar status
GET https://seu-backend-railway.railway.app/api/scraper/status
```

---

## 🧪 TESTE AGORA

```bash
# Terminal (substitua pela sua URL):
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Aguarde 3-5 minutos
sleep 180

# Verifique dados:
curl https://seu-backend-railway.railway.app/api/scraper/status

# Você deve ver: {"status": "ok", "database": {"events": 100, "odds": 400, ...}}
```

---

## ⚙️ CONFIGURAR N8N (10 MIN)

### Passo 1: Nova Schedule
```
Interval: 30 minutes
Cron: */30 * * * *
```

### Passo 2: HTTP Request
```
Method: POST
URL: https://seu-backend-railway.railway.app/api/trigger/all
Headers: Content-Type: application/json
```

### Passo 3: Ativar ✅

---

## 📊 RESULTADO ESPERADO

```
A cada 30 minutos:
├─ ~25 eventos do Betano
├─ ~18 eventos do Bet365
├─ ~31 eventos do Superbet
└─ ~22 eventos do EsportesDaSorte

Total: ~95 eventos por ciclo
Telegram: Notifica quando pronto
```

---

## 🔗 DOCUMENTAÇÃO COMPLETA

Se precisa de mais detalhes:

| Documento | Propósito |
|-----------|-----------|
| [RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) | Visão geral + 3 opções |
| [RAILWAY_SCRAPING_GUIDE.md](RAILWAY_SCRAPING_GUIDE.md) | Guia técnico completo |
| [RAILWAY_URLS_PRONTAS.md](RAILWAY_URLS_PRONTAS.md) | Endpoints + comandos |
| [CHECKLIST_IMPLEMENTACAO.md](CHECKLIST_IMPLEMENTACAO.md) | Passo-a-passo |
| [VALIDACAO_SCRAPING_RAILWAY.md](VALIDACAO_SCRAPING_RAILWAY.md) | Testar tudo |
| [ARQUITETURA_VISUAL.md](ARQUITETURA_VISUAL.md) | Diagramas |
| [INDICE_DOCUMENTACAO.md](INDICE_DOCUMENTACAO.md) | Índice completo |

---

## ❌ SE ALGO NÃO FUNCIONAR

```bash
# Health check
curl https://seu-backend-railway.railway.app/health

# Ver logs
railway logs --service backend --follow

# Se timeout, aumentar:
# railway env --update SCRAPER_TIMEOUT=600
```

---

## ✅ CHECKLIST

- [ ] Backend online? (curl /health)
- [ ] Scraper online? (curl /health)
- [ ] SCRAPER_API_URL configurado?
- [ ] Testou /api/trigger/all?
- [ ] Dados aparecem no status?
- [ ] Telegram recebeu notificação?
- [ ] N8N configurado?

---

## 🎯 RESUMO

| O quê | Onde | URL |
|------|------|-----|
| **Disparar** | Backend | POST `/api/trigger/all` |
| **Status** | Backend | GET `/api/scraper/status` |
| **Automação** | N8N | Schedule → HTTP Request |
| **Banco** | Railway Postgres | Dados salvos automaticamente |
| **Notificação** | Telegram Bot | Automático |

---

## 🚀 START AGORA

```bash
# 1. Teste manual
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# 2. Configure N8N (copie a URL acima)

# 3. Ative o workflow

# 4. Pronto! Roda sozinho a cada 30 min ✨
```

---

**Documentação criada em: Fevereiro 2026**  
**Para mais detalhes: Veja [INDICE_DOCUMENTACAO.md](INDICE_DOCUMENTACAO.md)**
