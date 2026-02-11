# 🏠 Sistema de Scrapers Locais - Guia Completo

## 🎯 Visão Geral

Sistema completo para coletar odds de casas de apostas **usando sua internet local (sem proxy)** e enviar os dados para a API no Railway.

## 📦 Componentes

### 1. Scrapers Locais (Python)
- **Betano**: ✅ Funcional
- **Esportes da Sorte**: ✅ Funcional  
- **Superbet**: ⚠️ Em desenvolvimento
- **Bet365**: ⚠️ Em desenvolvimento

### 2. API Local (FastAPI)
- Endpoint: `http://localhost:8000/api/trigger/local`
- Executa todos os scrapers e retorna JSON
- Envia dados para Railway automáticamente

### 3. n8n Workflows
- **Manual**: Execução sob demanda
- **Automático**: Cron (a cada 2h entre 10h-21h)

## 🚀 Como Usar

### Opção 1: Via Docker (Recomendado)

```powershell
# 1. Configure o .env.local
# Edite e adicione a URL da sua API no Railway
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper

# 2. Suba os containers
docker compose up -d

# 3. Acesse o n8n
# http://localhost:5679

# 4. Importe os workflows
# Vá em Workflows → Import from File
# Importe: n8n/workflows/Scraper Local Manual.json
# Importe: n8n/workflows/Scraper Local Automation.json

# 5. Teste manualmente primeiro
# Abra "Scraper Local Manual" e clique em "Execute Workflow"

# 6. Ative o automático
# Abra "Scraper Local Automation" e ative o toggle
```

### Opção 2: Diretamente com Python

```powershell
# 1. Instale dependências
pip install -r requirements.txt
playwright install chromium

# 2. Configure o .env.local
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper

# 3. Execute
python scrapers\local\run_all_local.py

# Ou no Windows
run_local_scraper.bat
```

### Opção 3: Via API HTTP

```powershell
# Se a API local estiver rodando em http://localhost:8000
curl.exe -X POST http://localhost:8000/api/trigger/local

# Ou
Invoke-RestMethod -Uri "http://localhost:8000/api/trigger/local" -Method Post
```

## 🔄 Fluxo Completo

```
┌─────────────────┐
│   n8n Trigger   │  ⏰ Cron: A cada 2h
│  (10h-21h)      │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│    HTTP POST Request    │
│ /api/trigger/local      │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│   API Local (FastAPI)   │  🐍 Container scraper-local
└────────┬────────────────┘
         │
         ├─→ Betano Local Scraper      ✅ Coleta dados
         ├─→ Superbet Local Scraper    ⚠️ Parser pendente
         ├─→ Esportes Local Scraper    ✅ Coleta dados
         └─→ Bet365 Local Scraper      ⚠️ Parser pendente
                    │
                    ↓
         ┌─────────────────────┐
         │  Formata dados      │
         │  (formato padrão)   │
         └──────────┬──────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │   POST para Railway │  ☁️ /api/odds/scraper
         │   (send_odds_to_api)│
         └──────────┬──────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │  PostgreSQL Railway │  💾 Salva no banco
         └─────────────────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │   n8n processa      │  📊 Formata resultado
         │   resposta JSON     │
         └─────────────────────┘
```

## 📊 Estrutura de Resposta da API

```json
{
  "triggered_at": "2026-02-11T18:30:00.000Z",
  "environment": "local",
  "proxy_enabled": false,
  "status": "success",
  "total_items": 13,
  "scrapers": {
    "betano": {
      "status": "success",
      "items": 8,
      "sent_to_api": true
    },
    "superbet": {
      "status": "warning",
      "items": 0,
      "message": "Nenhum dado coletado (parser pendente)"
    },
    "esportesdasorte": {
      "status": "success",
      "items": 5,
      "sent_to_api": true
    },
    "bet365": {
      "status": "warning",
      "items": 0,
      "message": "Nenhum dado coletado (parser pendente)"
    }
  }
}
```

## 🐳 Containers Docker

| Container | Porta | Descrição |
|-----------|-------|-----------|
| `leite-bets-local-scraper` | 8000 | API FastAPI com scrapers |
| `leite-bets-local-n8n` | 5679 | n8n para automação |

```powershell
# Ver containers rodando
docker ps

# Ver logs do scraper
docker logs leite-bets-local-scraper

# Ver logs do n8n
docker logs leite-bets-local-n8n

# Parar tudo
docker compose down

# Rebuildar e reiniciar
docker compose up -d --build
```

## ⏰ Agendamento

**Cron padrão:** `0 10-21/2 * * *`

**Execuções:**
- 10:00
- 12:00
- 14:00
- 16:00
- 18:00
- 20:00

**Modificar horário:**
1. Abra o workflow no n8n
2. Clique em "Schedule Trigger Local"
3. Modifique "Cron Expression"
4. Salve

**Exemplos:**
- `0 */3 * * *` - A cada 3 horas
- `0 8,12,16,20 * * *` - Às 8h, 12h, 16h e 20h
- `0 0 * * *` - Uma vez por dia (meia-noite)

## 🔍 Monitoramento

### Logs do Python

```powershell
# Container
docker logs leite-bets-local-scraper -f

# Script direto
python scrapers\local\run_all_local.py
```

### Logs do n8n

```
http://localhost:5679
→ Executions
→ Selecione uma execução
→ Veja detalhes de cada node
```

### Verificar API

```powershell
# Health check
curl http://localhost:8000/health

# Testar endpoint local
curl -X POST http://localhost:8000/api/trigger/local
```

## 🆚 Comparação: Local vs Railway

| Aspecto | Scrapers Locais | Scrapers Railway |
|---------|----------------|------------------|
| **Proxy** | ❌ Não usa | ✅ Webshare residencial |
| **Internet** | Sua conexão | Proxy rotativo |
| **Velocidade** | ⚡ Mais rápido | 🐢 Pode ser lento |
| **Custo** | 💰 Grátis | 💳 ~$5-10/mês (proxy) |
| **Bloqueios** | ⚠️ Risco maior | ✅ Risco menor |
| **Uso** | 🏠 Dev/teste local | ☁️ Produção |
| **Execução** | 🖥️ Sua máquina | ☁️ Nuvem 24/7 |

## ⚠️ Limitações

1. **Bloqueios de IP**: Sites podem bloquear se fazer muitas requisições
2. **Geolocalização**: Alguns sites exigem IP brasileiro
3. **Velocidade**: Depende da sua internet
4. **Disponibilidade**: Só funciona se sua máquina estiver ligada

## 💡 Dicas

1. **Não abuse**: Rode no máximo a cada 2-4 horas
2. **Use VPN BR**: Se estiver fora do Brasil
3. **Monitore logs**: Para detectar bloqueios cedo
4. **Teste manual**: Antes de ativar o automático
5. **Horário**: Rode em horários de baixo tráfego (10h-21h)

## 🐛 Troubleshooting

### ❌ "Connection refused" ao chamar API

**Causa**: Container não está rodando  
**Solução**:
```powershell
docker ps
docker logs leite-bets-local-scraper
docker compose restart scraper-local
```

### ❌ "API_URL não configurada"

**Causa**: `.env.local` não tem `API_URL`  
**Solução**:
```powershell
# Edite .env.local e adicione:
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper

# Reinicie container
docker compose restart scraper-local
```

### ❌ "Timeout" ao coletar

**Causa**: Site demorou muito ou bloqueou  
**Solução**:
- Aguarde algumas horas
- Use VPN
- Aumente timeout (180s padrão)

### ❌ Workflow não executa automaticamente

**Verificações**:
1. Workflow está ativo? (toggle verde)
2. Container n8n está rodando?
3. Expressão cron está correta?

```powershell
docker ps | Select-String "n8n"
docker logs leite-bets-local-n8n
```

### ⚠️ Dados não chegam no Railway

**Verificações**:
1. `API_URL` está correta?
2. Railway está acessível?
3. Logs mostram "sent_to_api: true"?

```powershell
# Teste a URL manualmente
curl https://seu-projeto.up.railway.app/health

# Veja logs do scraper
docker logs leite-bets-local-scraper | Select-String "enviado"
```

## 📚 Arquivos Importantes

```
leite-bets/
├── .env.local                          # ⚙️ Configurações
├── docker-compose.yml                  # 🐳 Containers
├── run_local_scraper.bat               # 🪟 Script Windows
├── QUICK_START_LOCAL.md                # 🚀 Guia rápido
│
├── scrapers/local/                     # 🏠 Scrapers sem proxy
│   ├── browser_no_proxy.py
│   ├── betano_local.py
│   ├── superbet_local.py
│   ├── esportesdasorte_local.py
│   ├── bet365_local.py
│   ├── run_all_local.py
│   └── README.md
│
├── scrapers/api/
│   └── routes.py                       # 🌐 Novo endpoint /api/trigger/local
│
└── n8n/workflows/
    ├── Scraper Local Manual.json       # 🖱️ Execução manual
    ├── Scraper Local Automation.json   # ⏰ Automático (cron)
    ├── README.md                       # 📖 Docs workflows
    └── IMPORTAR.md                     # 📥 Guia importação
```

## ✅ Checklist Final

- [ ] `.env.local` configurado com `API_URL`
- [ ] Containers rodando: `docker ps`
- [ ] n8n acessível: http://localhost:5679
- [ ] Workflows importados no n8n
- [ ] Teste manual executou com sucesso
- [ ] API Railway está acessível
- [ ] Logs mostram "jogos coletados"
- [ ] Dados chegaram no Railway
- [ ] Workflow automático ativado
- [ ] Monitoramento configurado

## 🎯 Próximos Passos

1. ✅ Complete a configuração (`API_URL`)
2. ✅ Teste com workflow manual
3. ✅ Verifique dados no Railway
4. ✅ Ative workflow automático
5. ✅ Monitore primeiras execuções
6. ⚠️ Implemente parsers Superbet/Bet365
7. 📧 Configure notificações (Telegram/Email)
8. 📊 Crie dashboard de monitoramento

## 📞 Suporte

- **Logs**: Sempre comece pelos logs
- **API**: Teste endpoints manualmente
- **n8n**: Use execuções manuais para debug
- **Docs**: Leia READMEs específicos de cada módulo

---

**🏆 Agora você tem um sistema completo de coleta de odds rodando localmente, enviando dados para a nuvem, tudo automatizado!**
