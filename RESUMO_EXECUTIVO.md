# 🚀 RESUMO EXECUTIVO - Como Executar a Raspagem no Railway

> Para: Seu Sócio / Gestor  
> De: Time Técnico  
> Data: Fevereiro 2026  
> Assunto: **Melhor forma de disparar raspagem no Railway**

---

## ⚡ RESPOSTA RÁPIDA

**A melhor forma é:** Usar **N8N com agendamento automático** que chama o Backend a cada 30 minutos.

```
N8N Scheduler (a cada 30 min)
    ↓
POST /api/trigger/all
    ↓
Backend inicia scrapers em background
    ↓
Telegram notifica quando pronto
    ↓
Dados salvos no banco
```

---

## 📊 Três Opções Disponíveis

| Opção | Melhor Para | Setup | Reliability |
|-------|-------------|-------|-------------|
| **1. N8N Automático** ✅ | **Produção** | Média | ⭐⭐⭐⭐⭐ |
| 2. N8N Manual | Testes | Baixa | ⭐⭐⭐ |
| 3. cURL Manual | Debug | Muito Baixa | ⭐⭐ |

---

## 1️⃣ OPÇÃO RECOMENDADA - N8N Automático

### O que é?
- **Agendador automático** que executa a cada 30 minutos
- Faz uma simples requisição HTTP para o Backend
- Backend coleta dados de 4 casas em paralelo
- Telegram notifica quando termina

### Como funciona?

```
┌─────────────┐
│   N8N Bot   │ ← Agendador automático
│ (a cada 30  │
│  minutos)   │
└──────┬──────┘
       │
       ├─ Faz requisição HTTP
       │  POST /api/trigger/all
       │
       ▼
┌──────────────────┐
│   Backend App    │ ← Recebe requisição
│ (Seu servidor)   │
└──────┬───────────┘
       │
       ├─ Retorna imediatamente
       │ (não bloqueia)
       │
       ├─ Dispara scrapers em background
       │
       ▼
┌────────────────────────────────────────┐
│   Scrapers rodam em paralelo (60-120s) │
│   • Betano: ~25 eventos                │
│   • Bet365: ~18 eventos                │
│   • Superbet: ~31 eventos              │
│   • EsportesDaSorte: ~22 eventos       │
└────────┬─────────────────────────────┘
         │
         ├─ Total: ~96 novos eventos
         │
         ▼
┌──────────────────┐
│  PostgreSQL DB   │ ← Salva dados
│  (Seu banco)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Telegram Bot    │ ← Notifica seu chat
│  (Automático)    │ "✅ 96 novos dados coletados!"
└──────────────────┘
```

### Vantagens ✅
- ✅ **Automático** - Não precisa fazer nada, roda sozinho
- ✅ **Confiável** - Se falhar, retenta automaticamente
- ✅ **Rápido** - Dados em 2 minutos
- ✅ **Escalável** - Funciona com 1 casa ou 100 casas
- ✅ **Monitorado** - Logs detalhados no Railway
- ✅ **Notificações** - Você recebe alertas no Telegram

### Desvantagens ❌
- ❌ Precisa de setup inicial (5 min)
- ❌ Depende de N8N rodando

---

## 2️⃣ OPÇÃO ALTERNATIVA - Manual cURL

Para **testes rápidos ou debug** sem N8N:

```bash
# Dispara manualmente a qualquer hora
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Resposta:
# {
#   "status": "triggered",
#   "message": "Scrapers iniciados em background"
# }

# Aguarde 2-3 minutos, depois:
curl https://seu-backend-railway.railway.app/api/scraper/status

# Você vê quantos dados foram coletados
```

### Vantagens ✅
- ✅ Simples, sem setup
- ✅ Útil para testes

### Desvantagens ❌
- ❌ Manual (precisa disparar manualmente)
- ❌ Sem automação
- ❌ Sem monitoria

---

## 🎯 SETUP PASSO A PASSO (15 MINUTOS)

### Passo 1: Verifique as URLs

No Railway Dashboard:

```
Backend URL:   https://seu-backend-railway.railway.app
Scraper URL:   https://seu-scraper-railway.railway.app
Database:      PostgreSQL (deve estar rodando)
```

### Passo 2: Configure Variáveis

No Backend Service (Railway → Variables):

```env
SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300
```

### Passo 3: Teste Manual

```bash
# Terminal, execute:
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Se retornar {"status": "triggered"} ✅ Pronto!
```

### Passo 4: Configure N8N (OPCIONAL)

No N8N, crie novo workflow:

1. **Schedule Trigger**
   - Cron: `*/30 * * * *` (a cada 30 min)

2. **HTTP Request**
   - Method: POST
   - URL: `https://seu-backend-railway.railway.app/api/trigger/all`

3. **Send Notification** (telegram)
   - Mensagem: `"✅ Raspagem disparada!"`

4. **Wait**
   - 2 minutos (deixar scrapers terminarem)

5. **Check Status**
   - GET: `https://seu-backend-railway.railway.app/api/scraper/status`

---

## 📞 URLs Prontas Para Usar

```bash
# Disparar raspagem
POST https://seu-backend-railway.railway.app/api/trigger/all

# Disparar apenas uma casa
POST https://seu-backend-railway.railway.app/api/trigger/betano
POST https://seu-backend-railway.railway.app/api/trigger/bet365
POST https://seu-backend-railway.railway.app/api/trigger/superbet
POST https://seu-backend-railway.railway.app/api/trigger/esportesdasorte

# Verificar status e quantos dados tem
GET https://seu-backend-railway.railway.app/api/scraper/status

# Health check
GET https://seu-backend-railway.railway.app/health
GET https://seu-scraper-railway.railway.app/health
```

---

## 📊 RESULTADOS ESPERADOS

### Após 1 requisição de trigger:

```
Eventos coletados:
├─ Betano: 20-30 eventos
├─ Bet365: 15-25 eventos
├─ Superbet: 25-35 eventos
└─ EsportesDaSorte: 20-30 eventos

Total: ~80-120 eventos novos por ciclo
Odds coletadas: ~300-400 odds novas
```

### Dashboard do seu banco (PostgreSQL):

```sql
SELECT COUNT(*) FROM events;        -- 150+ eventos
SELECT COUNT(*) FROM odds;          -- 450+ odds
SELECT COUNT(*) FROM arbitrages;    -- X% ROI encontrado
```

---

## 🔴 Se Algo Não Funcionar

### Problema 1: "Connection refused" ao trigger

```bash
# Verifique se Backend está online
curl https://seu-backend-railway.railway.app/health
# Deve retornar: {"status": "healthy"}
```

**Solução:** Reinicie Backend no Railway:
```bash
railway service restart backend
```

### Problema 2: Dados não salvam no banco

```bash
# Verifique se PostgreSQL está acessível
railway logs --service backend | grep "ERROR"
```

**Solução:** Verifique DATABASE_URL:
```bash
railway env --service backend | grep DATABASE_URL
```

### Problema 3: Timeout depois de 30 segundos

**Solução:** Aumentar timeout em N8N para 120 segundos

---

## ✅ CHECKLIST PRÉ-LANÇAMENTO

- [ ] Backend rodando no Railway
- [ ] Scraper rodando no Railway
- [ ] PostgreSQL acessível
- [ ] SCRAPER_API_URL configurado
- [ ] Testou `/api/trigger/all` com curl
- [ ] Dados apareceram no banco (após 3 min)
- [ ] N8N configurado com Schedule
- [ ] Telegram Bot Token configurado
- [ ] Recebeu notificação no Telegram
- [ ] Workflow do N8N ativado

---

## 📈 PRÓXIMOS PASSOS

1. **Hoje:** Configure N8N com agendamento (15 min)
2. **Amanhã:** Monitore primeira execução automática
3. **Esta semana:** Ajuste frequência conforme necessário
4. **Este mês:** Integre com dashboard de análise

---

## 🎯 RESUMO

| Pergunta | Resposta |
|----------|----------|
| Qual é a melhor forma? | **N8N automático a cada 30 min** |
| Quanto tempo de setup? | **15 minutos** |
| Funciona 24/7 sozinho? | **Sim** ✅ |
| Preciso fazer algo manual? | **Não** ✅ |
| Como sei se funcionou? | **Telegram notifica** ✅ |
| E se falhar? | **Railway relog, N8N retenta** ✅ |
| Qual o custo? | **Incluído no seu Railway** ✅ |

---

## 📚 Documentação Técnica

Para aprofundar, consulte:
- `RAILWAY_SCRAPING_GUIDE.md` - Guia completo
- `RAILWAY_URLS_PRONTAS.md` - URLs e comandos
- `ARQUITETURA_VISUAL.md` - Diagramas da arquitetura
- `VALIDACAO_SCRAPING_RAILWAY.md` - Testes de validação

---

## 👥 Suporte

- **Railway Dashboard:** https://railway.app
- **N8N Local:** http://localhost:5678 (ou seu endereço)
- **Logs:** `railway logs --service [backend|scraper]`

---

**Pronto para começar?** 🚀

Execute agora:
```bash
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all
```

Aguarde 3 minutos e veja os dados chegando! ✨
