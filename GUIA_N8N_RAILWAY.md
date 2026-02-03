# 🤖 GUIA: N8N no Railway - Automação de Scrapers

## 📋 RESUMO
Configurar N8N no Railway para disparar scrapers automaticamente a cada 30 minutos.

---

## 🚀 PASSO 1: CRIAR SERVIÇO N8N NO RAILWAY

### 1.1 No Railway Dashboard
1. Acesse: https://railway.app
2. Abra seu projeto **leite-bets**
3. Clique **"+ New"** → **"Empty Service"**
4. Nome: `n8n-automation`

### 1.2 Configurar Imagem Docker
1. Vá em **Settings** do serviço n8n-automation
2. Em **Source**, configure:
   - **Source Type**: Docker Image
   - **Image**: `n8nio/n8n:latest`

### 1.3 Adicionar Variáveis de Ambiente
Clique em **Variables** e adicione:

```env
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=SuaSenhaSegura123!
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n-automation-production-XXXX.up.railway.app/
GENERIC_TIMEZONE=America/Sao_Paulo
```

**⚠️ IMPORTANTE:**
- Troque `SuaSenhaSegura123!` por uma senha forte
- Após o deploy, atualize `WEBHOOK_URL` com a URL real do serviço

### 1.4 Configurar Porta
1. Em **Settings** → **Networking**
2. Configure **Port**: `5678`

### 1.5 Deploy
Clique **"Deploy"** e aguarde 2-3 minutos

---

## 🔧 PASSO 2: CRIAR WORKFLOW DE AUTOMAÇÃO

### 2.1 Acessar N8N
1. Após deploy, copie a URL: `https://n8n-automation-production-XXXX.up.railway.app`
2. Acesse no navegador
3. Login:
   - User: `admin`
   - Password: Senha que você configurou

### 2.2 Criar Novo Workflow
1. Clique **"New"** → **"Workflow"**
2. Nome: `Scraper Auto - Leite Bets`

### 2.3 Adicionar Nodes

#### NODE 1: Schedule Trigger
1. Clique **"+"** → Busque **"Schedule Trigger"**
2. Configure:
   - **Trigger Interval**: `Minutes`
   - **Minutes Between Triggers**: `30`
3. Clique **"Execute Node"** para testar

#### NODE 2: HTTP Request
1. Clique **"+"** após o Schedule
2. Busque **"HTTP Request"**
3. Configure:
   - **Method**: `POST`
   - **URL**: `https://leite-bets-production.up.railway.app/api/trigger/all`
   - **Timeout**: `180000` (3 minutos)
   - **Response Format**: `JSON`

#### NODE 3: Set (Formatação)
1. Clique **"+"** após HTTP Request
2. Busque **"Set"**
3. Configure campos:
   - **triggered_at**: `{{ $json.triggered_at }}`
   - **betano_status**: `{{ $json.scrapers.betano.status }}`
   - **betano_items**: `{{ $json.scrapers.betano.items }}`
   - **bet365_status**: `{{ $json.scrapers.bet365.status }}`
   - **bet365_items**: `{{ $json.scrapers.bet365.items }}`

#### NODE 4: Telegram (Opcional - Notificação)
Se quiser receber notificações:

1. Clique **"+"** após Set
2. Busque **"Telegram"**
3. Configure:
   - **Resource**: `Message`
   - **Operation**: `Send Text`
   - **Chat ID**: Seu Telegram Chat ID
   - **Text**:
   ```
   ✅ Scrapers executados!
   
   🕐 {{ $json.triggered_at }}
   
   📊 Betano: {{ $json.betano_items }} items
   📊 Bet365: {{ $json.bet365_items }} items
   ```

### 2.4 Salvar e Ativar
1. Clique **"Save"** (canto superior direito)
2. Toggle **"Active"** para ON
3. Workflow começa a rodar automaticamente!

---

## ✅ PASSO 3: VALIDAR FUNCIONAMENTO

### 3.1 Teste Manual
1. No workflow, clique **"Execute Workflow"**
2. Aguarde resposta (até 3 minutos)
3. Verifique se retornou dados dos scrapers

### 3.2 Verificar Logs
1. No N8N, vá em **"Executions"** (sidebar)
2. Veja histórico de execuções
3. Status verde = sucesso ✅

### 3.3 Validar no Backend
```powershell
# Verificar status do scraper
curl https://leite-bets-production.up.railway.app/api/scraper/status
```

---

## 📊 MONITORAMENTO

### Endpoints Úteis

#### Status Geral
```bash
GET https://leite-bets-production.up.railway.app/health
GET https://scraper-api-production-196e.up.railway.app/health
```

#### Trigger Manual (caso N8N falhe)
```bash
POST https://leite-bets-production.up.railway.app/api/trigger/all
POST https://leite-bets-production.up.railway.app/api/trigger/betano
POST https://leite-bets-production.up.railway.app/api/trigger/bet365
```

#### Status de Dados
```bash
GET https://leite-bets-production.up.railway.app/api/scraper/status
```

---

## 🔄 WORKFLOW ALTERNATIVO: INDIVIDUAL

Se preferir disparar scrapers separadamente (mais controle):

### Estrutura:
```
Schedule (30min)
  → HTTP: /api/trigger/betano
  → Delay (30s)
  → HTTP: /api/trigger/bet365
  → Delay (30s)
  → HTTP: /api/trigger/superbet
  → Delay (30s)
  → HTTP: /api/trigger/esportesdasorte
  → Telegram (resumo)
```

**Vantagem**: Controle fino por casa de apostas
**Desvantagem**: Mais complexo

---

## ⚠️ TROUBLESHOOTING

### N8N não acessa
- Verifique se porta 5678 está configurada
- Confirme variável `N8N_PORT=5678`
- Aguarde 2-3 min após deploy

### Workflow falha com timeout
- Aumente timeout do HTTP Request para 180000ms
- Alguns scrapers demoram até 2 minutos

### Scrapers retornam "no_data"
- Normal se não há jogos no momento
- Sites de apostas mudam layout frequentemente
- Scrapers precisam de manutenção periódica

### Backend retorna 502
- Verifique se `SCRAPER_API_URL` está configurada
- Confirme que tem `https://` na URL
- Verifique logs do Railway

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Configure N8N no Railway
2. ✅ Crie workflow de automação
3. ✅ Ative e teste
4. 📊 Monitor por 24h para validar estabilidade
5. 🔔 Configure alertas (Telegram/Email)
6. 🛠️ Ajuste frequência conforme necessário

---

## 📞 URLS IMPORTANTES

- **Backend**: https://leite-bets-production.up.railway.app
- **Scraper**: https://scraper-api-production-196e.up.railway.app
- **Bot**: https://service-bot-production-990d.up.railway.app
- **N8N**: https://n8n-automation-production-XXXX.up.railway.app (após criar)

---

## 💡 DICAS

- **Frequência ideal**: 15-30 minutos
- **Horário de pico**: 18h-23h (mais jogos)
- **Backup**: Mantenha trigger manual disponível
- **Logs**: Monitore Railway logs regularmente
- **Custos**: N8N + 3 serviços = ~$20-30/mês Railway

---

**🎉 Agora seu sistema está 100% automatizado!**
