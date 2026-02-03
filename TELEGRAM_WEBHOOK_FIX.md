# 🔧 Fix: Webhook do Telegram - Bad Request

## ❌ Problema Identificado

**Erro:** Bad Request / 401 Unauthorized na URL do webhook
**Causa:** Token do Telegram Bot **inválido ou revogado**

---

## ✅ Solução: Criar Novo Bot do Telegram

### Passo 1: Criar Bot com BotFather

1. **Abra o Telegram** e procure por [@BotFather](https://t.me/BotFather)

2. **Envie:** `/newbot`

3. **Escolha nome do bot:**
   ```
   Leite Bets Odds
   ```

4. **Escolha username (único):**
   ```
   leitebets_odds_bot
   ```
   *(Se já existir, tente: `leitebets_gabriel_bot`, `leitebets2026_bot`, etc)*

5. **Copie o token** que aparece:
   ```
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. **IMPORTANTE:** Configure privacidade do bot:
   ```
   /setprivacy
   [Selecione seu bot]
   Disable
   ```
   *(Permite que o bot leia todas as mensagens)*

---

### Passo 2: Configurar Token no N8N

1. **Acesse N8N:** https://n8n-production-ff57.up.railway.app

2. **Vá em:** Settings → Variables (ou Credentials)

3. **Adicione variável:**
   - **Nome:** `TELEGRAM_BOT_TOKEN`
   - **Valor:** Cole o token do BotFather

4. **Ou configure credenciais Telegram:**
   - Menu → Credentials → New
   - Type: Telegram
   - Access Token: Cole o token
   - Save

---

### ⚠️ Problema Conhecido: N8N Gera URL Sem `//`

Se o N8N gerar URLs no formato `https:n8n-production...` (sem `//`), **ignore o erro** e registre o webhook manualmente:

**Comando para registrar webhook manualmente:**
```powershell
# Cole no PowerShell
$token = "SEU_TOKEN_AQUI"
$webhookId = "WEBHOOK_ID_DO_N8N"  # Copie do nó Telegram Trigger
$webhookUrl = "https://n8n-production-ff57.up.railway.app/webhook/$webhookId/webhook"

# Registra webhook
$body = @{ url = $webhookUrl } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/setWebhook" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Verifica
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getWebhookInfo"
```

**Resultado esperado:**
```json
{
  "ok": true,
  "result": {
    "url": "https://n8n-production-ff57.up.railway.app/webhook/.../webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

### Passo 3: Atualizar Workflow

#### Opção A: Atualizar workflow existente

1. **Abra workflow:** Telegram Bot - Leite Bets

2. **Em cada nó que usa URL direta** (Olá, Liga, Jogo, Odd, HTTP Request7):
   
   **Troque:**
   ```
   https://api.telegram.org/bot8545930560:AAHAz7OjzpA6tqMcEb1bQfQkQoblmzzkrOg/sendMessage...
   ```
   
   **Por:**
   ```
   https://api.telegram.org/bot{{ $env.TELEGRAM_BOT_TOKEN }}/sendMessage...
   ```

3. **Salve workflow**

#### Opção B: Usar nós nativos do Telegram (RECOMENDADO)

Reimporte o workflow **telegram-bot.json** que criei, pois ele usa:
- Nós nativos do Telegram (não HTTP Request manual)
- Variáveis de ambiente automaticamente
- Melhor tratamento de erros

---

### Passo 4: Ativar Workflow e Registrar Webhook

1. **No N8N:**
   - Abra workflow Telegram Bot
   - Toggle **Active** = ON
   - N8N registra webhook automaticamente

2. **Verificar webhook registrado:**
   ```powershell
   # No PowerShell (substitua SEU_TOKEN pelo token novo)
   $token = "SEU_TOKEN_AQUI"
   Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getWebhookInfo"
   ```

3. **Resultado esperado:**
   ```json
   {
     "ok": true,
     "result": {
       "url": "https://n8n-production-ff57.up.railway.app/webhook/...",
       "has_custom_certificate": false,
       "pending_update_count": 0
     }
   }
   ```

---

### Passo 5: Testar Bot

1. **Procure seu bot no Telegram:**
   - Busque por `@leitebets_odds_bot` (ou o username que você escolheu)

2. **Envie:** `/start`

3. **Deve receber:**
   ```
   👋 Olá, [seu nome]!

   Bem-vindo ao seu Comparador de Odds...
   
   [🚀 Ver Campeonatos]
   ```

4. **Se não responder:**
   - Verifique Executions no N8N
   - Veja logs de erro
   - Confirme que workflow está Active

---

## 🔍 Diagnóstico de Problemas

### Problema: Webhook retorna 404

**Causa:** Workflow não está ativo

**Solução:**
1. N8N → Workflows → Telegram Bot
2. Toggle **Active** = ON
3. Aguarde 10 segundos
4. Teste novamente

---

### Problema: Bot não responde mensagens

**Causa 1:** Webhook não registrado

**Solução:**
```powershell
# Desregistrar webhook antigo
$token = "SEU_TOKEN"
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/deleteWebhook"

# Reativar workflow no N8N (toggle OFF → ON)
```

**Causa 2:** Privacidade do bot ativa

**Solução:**
1. BotFather → `/setprivacy`
2. Selecione bot → **Disable**

---

### Problema: Erro 401 Unauthorized

**Causa:** Token inválido/expirado

**Solução:**
- Gere novo bot com BotFather
- Atualize token no N8N

---

### Problema: Bad Request ao enviar mensagem

**Causa:** URL do webhook mal formatada

**URLs corretas:**
```
Test: https://n8n-production-ff57.up.railway.app/webhook-test/6c024d23-b98c-4a13-b8df-cdab775967c0
Prod: https://n8n-production-ff57.up.railway.app/webhook/6c024d23-b98c-4a13-b8df-cdab775967c0
```

**URLs ERRADAS** (falta `//`):
```
❌ https:n8n-production-ff57.up.railway.app/webhook/...
```

---

## 🧪 Comandos de Teste

### Verificar token do bot
```powershell
$token = "SEU_TOKEN"
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getMe"
```

**Resultado esperado:**
```json
{
  "ok": true,
  "result": {
    "id": 1234567890,
    "is_bot": true,
    "first_name": "Leite Bets Odds",
    "username": "leitebets_odds_bot"
  }
}
```

---

### Verificar webhook
```powershell
$token = "SEU_TOKEN"
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getWebhookInfo"
```

---

### Enviar mensagem de teste
```powershell
$token = "SEU_TOKEN"
$chatId = "SEU_CHAT_ID"  # Obtenha com @userinfobot
$body = @{
    chat_id = $chatId
    text = "🧪 Teste do bot Leite Bets"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/sendMessage" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 📋 Checklist de Verificação

Antes de testar, confirme:

- [ ] Novo bot criado com BotFather
- [ ] Token copiado corretamente (sem espaços)
- [ ] Privacidade do bot = Disabled
- [ ] Token configurado no N8N (variável ou credencial)
- [ ] Workflow importado (telegram-bot.json)
- [ ] Workflow ativo (toggle ON)
- [ ] URLs do webhook corretas (com `https://`)
- [ ] Enviou `/start` para o bot no Telegram

---

## 🚀 Próximos Passos

Após bot funcionando:

1. **Testar fluxo completo:**
   - Enviar mensagem → Ver campeonatos
   - Selecionar liga → Ver jogos
   - Selecionar jogo → Ver odds
   - Botão fechar

2. **Ajustar variáveis de ambiente:**
   ```bash
   TELEGRAM_BOT_TOKEN=novo_token_aqui
   TELEGRAM_CHAT_ID=seu_chat_id  # Para notificações
   ```

3. **Ativar Scraper Automation:**
   - Workflow separado para coleta automática
   - Executa independente do bot Telegram

4. **Monitorar:**
   - N8N → Executions
   - Railway → Backend logs
   - Telegram → Mensagens do bot

---

## 💡 Dica: Usar Nós Nativos do Telegram

O workflow **telegram-bot.json** usa nós nativos do N8N em vez de HTTP Request manual:

**Vantagens:**
- ✅ Webhook configurado automaticamente
- ✅ Usa credenciais centralizadas
- ✅ Melhor tratamento de erros
- ✅ Não precisa construir URLs manualmente
- ✅ Suporte a todas features do Telegram (inline keyboards, etc)

**Importar:**
1. N8N → Import from File
2. Selecione `telegram-bot.json`
3. Configure credenciais Telegram
4. Ative workflow

---

**Última atualização:** 03/02/2026

**Precisa de ajuda?** Verifique logs do N8N (Executions) ou Railway (Backend service)
