# ✅ Checklist de Implementação - Railway Scraping

> Guia prático para implementar a solução passo a passo

---

## 🎯 FASE 1: PRÉ-REQUISITOS (5 MIN)

```
☐ Tenho acesso ao Railway Dashboard
☐ Backend está ativo no Railway
☐ Scraper está ativo no Railway  
☐ PostgreSQL está ativo no Railway
☐ Tenho as URLs dos serviços:
   ☐ Backend: https://...
   ☐ Scraper: https://...
   ☐ Database: postgresql://...
☐ Bot do Telegram está configurado
☐ Posso acessar N8N (local ou railway)
```

**Próximo:** Ir para FASE 2

---

## 🔧 FASE 2: CONFIGURAR BACKEND (10 MIN)

### 2.1 Adicionar Variáveis de Ambiente

**Local:** Railway → Seu Projeto → Backend Service → Variables

```env
# Adicionar estas variáveis se não existirem:

SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300
LOG_LEVEL=info
```

```
☐ SCRAPER_API_URL configurado
☐ SCRAPER_TIMEOUT setado para 300
☐ LOG_LEVEL setado para info
☐ Cliquei em "Update Variables"
☐ Backend foi reiniciado automaticamente
```

### 2.2 Adicionar Código dos Endpoints

**Opção A - Já está implementado?**

Verifique se `backend/main.py` já tem:
- ✅ `@app.post("/api/trigger/all")`
- ✅ `@app.post("/api/trigger/{scraper_name}")`
- ✅ `@app.get("/api/scraper/status")`

Se NÃO tem:

```
☐ Copie o código de EXEMPLO_TRIGGER_BACKEND.py
☐ Cole em backend/main.py (após os imports)
☐ Adicione a importação: from fastapi import BackgroundTasks
☐ Teste localmente: python main.py
☐ Se funcionar, commit e push para Railway
```

Se JÁ tem:

```
☐ Endpoints já existem ✅
☐ Pule para FASE 3
```

---

## 🔗 FASE 3: VALIDAR CONECTIVIDADE (10 MIN)

### 3.1 Backend Health Check

```bash
# Execute em um terminal:
curl https://seu-backend-railway.railway.app/health

# Resposta esperada:
# {"status": "healthy"}
```

```
☐ Backend responde com status 200
☐ Resposta contém "healthy"
```

### 3.2 Scraper Health Check

```bash
curl https://seu-scraper-railway.railway.app/health

# Resposta esperada:
# {"status": "ok"}
```

```
☐ Scraper responde com status 200
☐ Resposta contém "ok"
```

### 3.3 Database Status

```bash
curl https://seu-backend-railway.railway.app/api/scraper/status

# Resposta esperada:
# {
#   "status": "ok",
#   "database": {
#     "events": 0,
#     "odds": 0,
#     ...
#   }
# }
```

```
☐ Status retorna "ok"
☐ Database acessível
☐ Mostra número de eventos/odds atuais
```

---

## 🚀 FASE 4: TESTE MANUAL (5 MIN)

### 4.1 Dispara Trigger Manualmente

```bash
# Execute:
curl -X POST https://seu-backend-railway.railway.app/api/trigger/all

# Resposta esperada:
# {
#   "status": "triggered",
#   "message": "Scrapers iniciados em background"
# }
```

```
☐ Requisição retorna status 200
☐ Response contém "triggered"
☐ Não tive timeout (menos de 5 segundos)
```

### 4.2 Aguarde Execução

```bash
# Aguarde 3-5 minutos (scrapers rodam em background)
echo "Aguardando scrapers... (3-5 min)"
sleep 180

# Verifique status novamente:
curl https://seu-backend-railway.railway.app/api/scraper/status
```

```
☐ Dados aumentaram em eventos
☐ Dados aumentaram em odds
☐ "last_scrape" tem timestamp recente
☐ Nenhum erro nos logs

☐ (OPCIONAL) Verifique Telegram:
   ☐ Recebeu notificação do bot
   ☐ Mostra número de eventos coletados
```

---

## 📅 FASE 5: CONFIGURAR N8N (10 MIN)

### 5.1 Acesse N8N

```
URL: http://localhost:5678
ou
URL: (se Railway) https://seu-n8n-railway.railway.app
```

```
☐ N8N está acessível
☐ Consigo fazer login
```

### 5.2 Criar Novo Workflow

Clique em **"New" → "Workflow"**

```
☐ Workflow criado
☐ Está em modo de edição
```

### 5.3 Adicionar Schedule Trigger

**Node 1: Schedule Trigger**

1. Clique "Add Node"
2. Procure por "Schedule"
3. Selecione "Schedule Trigger"

**Configurar:**
- Mode: Cron
- Cron: `*/30 * * * *` (a cada 30 minutos)

```
☐ Schedule Trigger adicionado
☐ Cron configurado para */30 * * * *
```

### 5.4 Adicionar HTTP Request

**Node 2: HTTP Request**

1. Clique "Add Node" novamente
2. Procure por "HTTP"
3. Selecione "HTTP Request"

**Configurar:**

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `https://seu-backend-railway.railway.app/api/trigger/all` |
| Headers | `Content-Type: application/json` |
| Timeout | 30 |

```
☐ HTTP Request adicionado
☐ Method = POST
☐ URL apontando para backend correto
☐ Headers configurados
☐ Timeout = 30 segundos
```

### 5.5 Adicionar Notificação (OPCIONAL)

**Node 3: Telegram Notification**

1. Clique "Add Node"
2. Procure por "Telegram"
3. Selecione "Telegram"

**Configurar:**
- Bot Token: `TELEGRAM_BOT_TOKEN`
- Chat ID: `TELEGRAM_CHAT_ID`
- Message: `"✅ Raspagem disparada! Aguarde..."`

```
☐ Telegram node adicionado
☐ Token configurado
☐ Chat ID configurado
☐ Mensagem customizada (opcional)
```

### 5.6 Salvar e Ativar

1. Clique "Save" (Ctrl+S)
2. Dê um nome: "Leite Bets - Raspagem Automática"
3. Clique "Activate" para ligar

```
☐ Workflow salvo com nome descritivo
☐ Workflow ativado (toggle azul)
☐ Vejo "Active" no topo
```

---

## 🧪 FASE 6: TESTE E VALIDAÇÃO (10 MIN)

### 6.1 Execute Workflow Manualmente

No N8N:
1. Clique "Execute Workflow"
2. Aguarde conclusão

```
☐ Workflow executa sem erros
☐ HTTP Request retorna 200
☐ Response contém "triggered"
☐ Todos os nodes ficar verdes ✅
```

### 6.2 Monitore Execução

```bash
# Em um terminal, veja logs em tempo real:
railway logs --service backend --follow
```

```
☐ Logs mostram "🔄 Iniciando raspagem..."
☐ Logs mostram "📊 Triggering betano..."
☐ Logs mostram "✅ betano: X items coletados"
☐ Nenhum "❌ ERROR" nos logs
```

### 6.3 Verifique Dados

```bash
# Após 3-5 minutos:
curl https://seu-backend-railway.railway.app/api/scraper/status
```

```
☐ Events aumentou
☐ Odds aumentou
☐ Last_scrape tem timestamp recente
```

---

## 📊 FASE 7: CONFIGURAÇÃO AVANÇADA (OPCIONAL)

### 7.1 Adicionar Wait Node

Entre HTTP Request e próximos nodes:

1. Clique "Add Node"
2. Procure por "Wait"
3. Selecione "Wait"

**Configurar:**
- Wait for: 2 minutes (deixar scrapers terminarem)

```
☐ Wait node adicionado
☐ Configurado para 2 minutos
```

### 7.2 Adicionar Verificação de Status

Após o Wait:

1. Clique "Add Node"
2. Procure por "HTTP"
3. Selecione "HTTP Request" novamente

**Configurar:**
- Method: GET
- URL: `https://seu-backend-railway.railway.app/api/scraper/status`

```
☐ GET Status node adicionado
☐ Apontando para /api/scraper/status
```

### 7.3 Adicionar Notificação de Conclusão

**Node: Telegram Notification**

- Message: `"✅ Raspagem concluída!
           Total: {{$node["HTTP Request2"].json.database.events}} eventos"`

```
☐ Notificação de sucesso configurada
☐ Mostra número de eventos coletados
```

---

## 🔍 FASE 8: MONITORAMENTO CONTÍNUO (APÓS SETUP)

### 8.1 Dashboard N8N

```
☐ Verifique "Executions" regularmente
☐ Todos os runs com status "success"
☐ Se falha, clique para ver erro
```

### 8.2 Logs Railway

```bash
# Diariamente (ou conforme necessário):
railway logs --service backend --since "2h ago"
```

```
☐ Nenhum "❌ ERROR" crítico
☐ Cada 30 min tem "✅" de sucesso
☐ Last_scrape sempre recent
```

### 8.3 Telegram Notifications

```
☐ Recebo notificação a cada ciclo
☐ Números de dados aumentam
☐ Se falha, recebo alerta
```

---

## 📈 FASE 9: TROUBLESHOOTING

Se algo não funcionar:

### Problema: "Connection refused"

```bash
# Passo 1: Verifique health
curl https://seu-backend-railway.railway.app/health

# Passo 2: Se erro, verifique logs
railway logs --service backend --tail 50

# Passo 3: Se não apareça, reinicie
railway service restart backend

# Passo 4: Aguarde 30s e teste novamente
```

```
☐ Health check passando
☐ Backend respondendo
```

### Problema: "Timeout"

```bash
# Verifique SCRAPER_API_URL
railway env --service backend | grep SCRAPER_API_URL

# Se vazio ou errado, atualize:
railway env --update SCRAPER_API_URL=https://seu-scraper-url
```

```
☐ SCRAPER_API_URL configurado
☐ Aponta para scraper correto
```

### Problema: "Dados não salvam"

```bash
# Verifique DATABASE_URL
railway env --service backend | grep DATABASE_URL

# Teste conexão:
psql "$DATABASE_URL" -c "SELECT 1"
```

```
☐ DATABASE_URL válida
☐ PostgreSQL respondendo
```

---

## ✅ FASE FINAL: CHECKLIST COMPLETO

Marque como COMPLETO:

```
═══════════════════════════════════════════════════════════════

✓ INFRASTRUCTURE
  ☐ Backend online e respondendo
  ☐ Scraper online e respondendo
  ☐ PostgreSQL acessível
  ☐ Variáveis de ambiente configuradas

✓ ENDPOINTS
  ☐ POST /api/trigger/all implementado
  ☐ GET /api/scraper/status implementado
  ☐ Health checks funcionando

✓ FUNCIONALIDADE
  ☐ Trigger manual funciona
  ☐ Dados salvam no banco
  ☐ Bot envia notificações

✓ AUTOMAÇÃO
  ☐ N8N workflow criado
  ☐ Schedule trigger configurado
  ☐ HTTP request apontando certo

✓ VALIDAÇÃO
  ☐ Teste completo executado
  ☐ Dados aparecem após 3-5 min
  ☐ Telegram recebe notificações
  ☐ Logs não mostram erros críticos

═══════════════════════════════════════════════════════════════

🎉 PRONTO PARA PRODUÇÃO!
```

---

## 🚀 PRÓXIMOS PASSOS

- [ ] **Hoje:** Complete este checklist
- [ ] **Amanhã:** Monitore primeira execução automática
- [ ] **Esta semana:** Ajuste frequência conforme necessário
- [ ] **Este mês:** Implemente dashboard de análise

---

## 📞 SUPORTE RÁPIDO

| Dúvida | Resposta |
|--------|----------|
| Qual URL usar? | Copie do Railway Dashboard |
| Qual timeout? | 300 segundos (5 minutos) |
| Quanto tempo demora? | 2-3 minutos por ciclo |
| Posso mudar frequência? | Sim, mude o cron no N8N |
| E se falhar? | N8N retenta, você recebe alerta |
| Preciso de mais informações? | Veja: `RAILWAY_SCRAPING_GUIDE.md` |

---

**Sucesso! Você agora tem scrapin automático rodando 24/7!** ✨
