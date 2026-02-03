# Workflows N8N - Leite Bets

Este documento descreve os 2 workflows separados que compõem a automação do sistema de arbitragem de apostas.

## 📋 Índice
- [Workflow 1: Scraper Automation](#workflow-1-scraper-automation)
- [Workflow 2: Telegram Bot](#workflow-2-telegram-bot)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Importação no N8N](#importação-no-n8n)

---

## 🤖 Workflow 1: Scraper Automation

**Arquivo:** `scraper-automation.json`

### Objetivo
Executa automaticamente todos os scrapers em horários programados, coletando odds de todas as casas de apostas.

### Fluxo de Execução

```
Schedule Trigger (Cron)
    ↓
Trigger All Scrapers (POST /api/trigger/all)
    ↓
Format Result (Processa resposta)
    ↓
All Success? (Verifica resultado)
    ↓           ↓
Notify Success   Notify Failures
```

### Nós do Workflow

#### 1. **Schedule Trigger**
- **Tipo:** Schedule Trigger
- **Configuração:** `0 10-21/2 * * *`
- **Descrição:** Executa a cada 2 horas entre 10h e 21h
- **Ajuste recomendado:** Modifique conforme necessidade (ex: `*/30 10-21 * * *` para 30 minutos)

#### 2. **Trigger All Scrapers**
- **Tipo:** HTTP Request
- **Método:** POST
- **URL:** `https://leite-bets-production.up.railway.app/api/trigger/all`
- **Timeout:** 180 segundos (3 minutos)
- **Response Format:** JSON
- **Descrição:** Chama o endpoint do backend que dispara todos os 4 scrapers simultaneamente

#### 3. **Format Result**
- **Tipo:** Code (JavaScript)
- **Descrição:** Analisa resultado dos scrapers e formata mensagem legível
- **Output:**
  - `mensagem`: Texto formatado para Telegram
  - `sucessos`: Quantidade de scrapers bem-sucedidos
  - `falhas`: Quantidade de scrapers com erro
  - `totalScrapers`: Total de scrapers executados

**Exemplo de mensagem gerada:**
```
🎉 Execução de Scrapers - 03/02/2026 15:30:45

📊 Resumo:
• Total: 4 scrapers
• Sucessos: 3
• Falhas: 1

📝 Detalhes:
✅ betano: 3 items
✅ bet365: 0 items
❌ superbet: Expecting value: line 1 column 1 (char 0)...
✅ esportesdasorte: 5 items

_Próxima execução em 2 horas_
```

#### 4. **All Success?**
- **Tipo:** IF Node
- **Condição:** `totalScrapers === sucessos`
- **Descrição:** Verifica se todos os scrapers funcionaram corretamente

#### 5. **Notify Success** / **Notify Failures**
- **Tipo:** Telegram
- **Descrição:** Envia notificação via Telegram (opcional - pode ser desativado)
- **Parse Mode:** Markdown
- **Nota:** Requer configuração de credenciais e TELEGRAM_CHAT_ID

### Resposta da API

```json
{
  "triggered_at": "2026-02-03T18:27:23.662149",
  "scraper_url": "https://scraper-api-production-196e.up.railway.app",
  "scrapers": {
    "betano": {
      "status": "success",
      "status_code": 200,
      "items": 3
    },
    "bet365": {
      "status": "success",
      "status_code": 200,
      "items": 0
    },
    "superbet": {
      "status": "error",
      "error": "Parsing error"
    },
    "esportesdasorte": {
      "status": "success",
      "status_code": 200,
      "items": 5
    }
  }
}
```

---

## 💬 Workflow 2: Telegram Bot

**Arquivo:** `telegram-bot.json`

### Objetivo
Permite que usuários interajam com o bot do Telegram para consultar odds em tempo real, navegando por campeonatos e jogos.

### Fluxo de Execução

```
Telegram Trigger (Mensagem/Callback)
    ↓
Router (Switch por tipo)
    ↓
┌────────────┬──────────────┬─────────────┬────────────┐
│  Message   │   Button     │   League    │    Game    │
│   Text     │   (btn_1)    │  (league_X) │  (game_X)  │
└─────┬──────┴──────┬───────┴──────┬──────┴──────┬─────┘
      ↓             ↓              ↓             ↓
  Send Welcome  Fetch Leagues  Fetch Games  Fetch Odds
                     ↓              ↓             ↓
              Format Leagues  Format Games  Format Odds
                     ↓              ↓             ↓
              Send Leagues    Send Games    Send Odds
```

### Nós do Workflow

#### 1. **Telegram Trigger**
- **Tipo:** Telegram Trigger
- **Updates:** `message`, `callback_query`
- **Descrição:** Recebe mensagens de texto e cliques em botões inline
- **Credenciais:** Requer configuração do bot do Telegram

#### 2. **Router (Switch)**
- **Tipo:** Switch
- **Descrição:** Direciona fluxo baseado no tipo de interação
- **Outputs:**
  - `message`: Mensagem de texto (qualquer texto enviado)
  - `button`: Callback com `btn_` (botão "Ver Campeonatos")
  - `league`: Callback com `league_X` (seleção de campeonato)
  - `game`: Callback com `game_X` (seleção de jogo)
  - `close`: Callback `fechar` (fechar conversa)

#### 3. **Send Welcome**
- **Tipo:** Telegram
- **Trigger:** Mensagem de texto
- **Descrição:** Envia mensagem de boas-vindas com botão "Ver Campeonatos"
- **Inline Keyboard:** `[["🚀 Ver Campeonatos" → btn_1]]`

#### 4. **Fetch Leagues → Format Leagues → Send Leagues**
- **Trigger:** Callback `btn_1`
- **API Call:** `GET /api/events`
- **Processamento:**
  - Extrai ligas únicas dos eventos
  - Cria botões inline para cada campeonato
  - Envia mensagem "Selecione um campeonato..."
- **Inline Keyboard:** `[["⚽ Liga A" → league_Liga A], ["⚽ Liga B" → league_Liga B], ...]`

#### 5. **Fetch Games → Format Games → Send Games**
- **Trigger:** Callback `league_X`
- **API Call:** `GET /api/events`
- **Processamento:**
  - Filtra jogos da liga selecionada
  - Remove duplicatas por `eventId`
  - Cria botões inline para cada jogo
  - Adiciona botão "Voltar"
- **Inline Keyboard:** 
  ```
  [["🏟️ Time A x Time B" → game_123],
   ["🏟️ Time C x Time D" → game_456],
   ["⬅️ Voltar" → btn_1]]
  ```

#### 6. **Fetch Odds → Format Odds → Send Odds**
- **Trigger:** Callback `game_X`
- **API Call:** `GET /api/events`
- **Processamento:**
  - Busca evento específico por `eventId`
  - Formata odds de todas as casas de apostas
  - Edita mensagem anterior (não cria nova)
- **Inline Keyboard:**
  ```
  [["⬅️ Voltar para Liga X" → league_Liga X],
   ["🏠 Início" → btn_1, "❌ Fechar" → fechar]]
  ```

**Exemplo de mensagem de odds:**
```markdown
📊 *ODDS: Flamengo x Corinthians*
🏆 Liga: Brasileirão Série A

📍 *Betano*
  • Casa: 1.85
  • Empate: 3.40
  • Fora: 4.20
  • 1X: 1.25 | X2: 2.10

📍 *Bet365*
  • Casa: 1.90
  • Empate: 3.30
  • Fora: 4.00
  • 1X: 1.22 | X2: 2.05

_🕒 Atualizado: 15:30:45_
```

#### 7. **Close Conversation**
- **Trigger:** Callback `fechar`
- **Descrição:** Edita mensagem removendo botões
- **Mensagem:** "Consulta finalizada. Quando precisar de novas odds, é só chamar! 👋"

---

## ⚙️ Variáveis de Ambiente

Configure no N8N (Settings → Environments):

### Obrigatórias

```bash
# Backend API
BACKEND_API_URL=https://leite-bets-production.up.railway.app

# Telegram Bot (apenas para Workflow 2)
TELEGRAM_BOT_TOKEN=8545930560:AAHAz7OjzpA6tqMcEb1bQfQkQoblmzzkrOg

# Telegram Chat ID (apenas para notificações do Workflow 1)
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### Como obter TELEGRAM_CHAT_ID

1. Abra conversa com [@userinfobot](https://t.me/userinfobot)
2. Envie `/start`
3. Copie o ID que aparece

---

## 📥 Importação no N8N

### Passo 1: Acessar N8N
```
https://n8n-automation-production-XXXX.up.railway.app
```

### Passo 2: Importar Workflows

1. Clique em **Workflows** → **Import from File**
2. Selecione `scraper-automation.json`
3. Repita para `telegram-bot.json`

### Passo 3: Configurar Credenciais (Workflow 2)

1. Abra workflow **Telegram Bot**
2. Clique em qualquer nó Telegram
3. Configure credenciais:
   - **Name:** Telegram Bot
   - **Access Token:** `TELEGRAM_BOT_TOKEN` (use variável de ambiente)
4. Salve

### Passo 4: Testar Workflows

#### Scraper Automation:
1. Abra workflow
2. Clique em **Execute Workflow** (botão play)
3. Aguarde 3-5 minutos
4. Verifique output do nó "Format Result"

#### Telegram Bot:
1. Abra workflow
2. Ative workflow (toggle **Active**)
3. Configure webhook automático
4. Envie mensagem para seu bot no Telegram
5. Deve receber mensagem de boas-vindas

### Passo 5: Ativar Scraper Automation

1. Abra workflow **Scraper Automation**
2. Toggle **Active** para ON
3. Próxima execução ocorrerá no horário programado
4. Verifique em **Executions** → histórico de execuções

---

## 🔧 Ajustes e Personalização

### Modificar Frequência de Execução

Edite o nó **Schedule Trigger** no workflow 1:

```bash
# A cada 30 minutos entre 10h e 21h
*/30 10-21 * * *

# A cada 1 hora entre 8h e 23h
0 8-23 * * *

# A cada 15 minutos o dia todo
*/15 * * * *

# Apenas dias úteis (seg-sex) a cada 2 horas
0 10-21/2 * * 1-5
```

### Desativar Notificações Telegram (Workflow 1)

Duas opções:

1. **Remover nós de notificação:**
   - Delete nós "Notify Success" e "Notify Failures"

2. **Desconectar nós:**
   - Remova conexões do nó "All Success?" para os nós de notificação

### Adicionar Mais Casas de Apostas

O workflow se adapta automaticamente quando novos scrapers são adicionados ao backend. Nenhuma modificação necessária no N8N.

---

## 📊 Monitoramento

### Verificar Execuções

1. N8N → **Executions**
2. Filtre por workflow
3. Verifique status (Success/Error)
4. Clique para ver detalhes

### Logs do Backend (Railway)

```bash
# Acesse Railway dashboard
https://railway.app → leite-bets → backend

# View Logs
# Procure por:
# - "POST /api/trigger/all" - requisições do N8N
# - "Triggering scraper" - scrapers sendo executados
# - "Error" - erros de execução
```

### Health Checks

```bash
# Backend
curl https://leite-bets-production.up.railway.app/health

# Scraper
curl https://scraper-api-production-196e.up.railway.app/health

# N8N
curl https://n8n-automation-production-XXXX.up.railway.app/healthz
```

---

## 🐛 Troubleshooting

### Scraper Automation não executa

1. **Verificar se workflow está ativo:**
   - Toggle "Active" deve estar ON
   - Ícone verde ao lado do nome

2. **Verificar Schedule Trigger:**
   - Clique no nó → verifique expressão cron
   - Use [Crontab Guru](https://crontab.guru/) para validar

3. **Testar manualmente:**
   - Clique "Execute Workflow"
   - Veja output de cada nó

### Telegram Bot não responde

1. **Verificar webhook:**
   - N8N → Workflow → Settings → Webhook URL
   - Deve estar configurado automaticamente

2. **Verificar credenciais:**
   - Nó Telegram → Credentials
   - Token deve estar correto

3. **Testar com [@userinfobot](https://t.me/userinfobot):**
   - Confirme que seu bot está ativo

### Timeout no Trigger All Scrapers

**Causa:** Scrapers demoram mais de 3 minutos

**Solução:**
1. Edite nó "Trigger All Scrapers"
2. Options → Timeout: `300000` (5 minutos)
3. Ou `600000` (10 minutos) se necessário

### Erro "No scheme supplied"

**Causa:** URL sem `https://`

**Solução:**
1. Verifique variável `BACKEND_API_URL` em N8N
2. Deve incluir protocolo: `https://leite-bets-production.up.railway.app`

---

## 🚀 Próximos Passos

1. ✅ Importar workflows no N8N
2. ✅ Configurar variáveis de ambiente
3. ✅ Configurar credenciais Telegram
4. ✅ Testar ambos workflows manualmente
5. ✅ Ativar Scraper Automation
6. ✅ Monitorar primeiras execuções
7. 📊 Analisar logs após 24 horas
8. 🔧 Ajustar frequência conforme necessário

---

## 📚 Recursos Adicionais

- [N8N Documentation](https://docs.n8n.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Cron Expression Generator](https://crontab.guru/)
- [Railway Documentation](https://docs.railway.app/)

---

**Última atualização:** 03/02/2026
