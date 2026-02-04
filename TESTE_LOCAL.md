# 🧪 Teste Local do Scraper

Este guia mostra como testar o scraper localmente e depois migrar para o modo híbrido (scraper local → Railway backend).

## 🔧 Configuração Inicial

### 1. Preparar ambiente

```powershell
# Copiar arquivo de exemplo
Copy-Item .env.local .env

# Editar .env e adicionar seu TELEGRAM_CHAT_ID
notepad .env
```

### 2. Iniciar stack local

```powershell
# Build e start todos os serviços
docker-compose up --build -d

# Ver logs em tempo real
docker-compose logs -f scraper
```

### 3. Testar scraper

```powershell
# Testar EsportesDaSorte
Invoke-RestMethod -Uri 'http://localhost:8001/scrape/esportesdasorte' -Method POST

# Ver screenshot e HTML capturados
start storage/debug/esportesdasorte_simple.png
start storage/debug/esportesdasorte_simple.html
```

### 4. Verificar dados no banco local

```powershell
# Conectar ao PostgreSQL local
docker exec -it betting-bot-db psql -U postgres -d betting_bot

# Ver eventos cadastrados
SELECT id, home_team, away_team, event_date FROM events LIMIT 10;

# Sair
\q
```

## 🔄 Modo Híbrido (Scraper Local → Railway)

Uma vez que o scraper estiver funcionando localmente:

### 1. Atualizar configuração

```powershell
# Editar docker-compose.yml
notepad docker-compose.yml
```

Altere a seção do scraper:

```yaml
environment:
  # Comentar API local
  # - API_URL=http://api:8000/api/odds/scraper
  
  # Descomentar API Railway
  - API_URL=https://leite-bets-production.up.railway.app/api/odds/scraper
  - DISABLE_PROXY=true
```

### 2. Reiniciar scraper

```powershell
# Restart apenas o scraper
docker-compose restart scraper

# Ver logs
docker-compose logs -f scraper
```

### 3. Testar envio para Railway

```powershell
# Testar scraper (agora envia para Railway)
Invoke-RestMethod -Uri 'http://localhost:8001/scrape/esportesdasorte' -Method POST

# Verificar logs do Railway
# Acessar: https://railway.app/project/seu-projeto/service/leite-bets
```

### 4. Verificar dados no Railway

```powershell
# Conectar ao PostgreSQL Railway (ajustar credenciais)
# Obter string de conexão em: https://railway.app/project/seu-projeto/service/postgres
psql "postgresql://usuario:senha@host:porta/railway"

# Ver eventos
SELECT COUNT(*) FROM events;
```

## 📊 Estrutura de Testes

```
Fase 1: Teste Local Puro
┌─────────────┐      ┌─────────┐      ┌──────────┐
│   Scraper   │─────▶│   API   │─────▶│ Postgres │
│  (Docker)   │      │ (Docker)│      │ (Docker) │
└─────────────┘      └─────────┘      └──────────┘
     ↓
  storage/debug/
  (screenshots e HTML)

Fase 2: Modo Híbrido
┌─────────────┐                       ┌───────────────┐
│   Scraper   │──────────────────────▶│  API Railway  │
│  (Docker    │      HTTPS            │               │
│   Local)    │                       │  Postgres     │
└─────────────┘                       │  Railway      │
     ↓                                └───────────────┘
  storage/debug/
  (análise local)
```

## 🐛 Debug

### Ver estrutura HTML capturada

```powershell
# Abrir HTML no browser
start storage/debug/esportesdasorte_simple.html

# Ver seletores usados nos logs
docker-compose logs scraper | Select-String "Seletor"
```

### Ver screenshot

```powershell
# Screenshot da página carregada
start storage/debug/esportesdasorte_simple.png

# Screenshot quando não encontra jogos
start storage/debug/esportesdasorte_no_games.png
```

### Ver logs detalhados

```powershell
# Logs do scraper
docker-compose logs -f scraper

# Logs da API
docker-compose logs -f api

# Todos os logs
docker-compose logs -f
```

## 🎯 Próximos Passos

1. ✅ Testar localmente e capturar screenshots/HTML
2. ✅ Analisar DOM e ajustar seletores
3. ✅ Fazer scraper funcionar localmente
4. ✅ Configurar modo híbrido (local → Railway)
5. ⏳ Testar com proxies Webshare
6. ⏳ Deploy scraper para Railway (quando proxies funcionarem)

## 📝 Notas

- **storage/debug/** é montado como volume - arquivos acessíveis no Windows
- Scraper roda na porta **8001** localmente
- API local roda na porta **8000**
- PostgreSQL local roda na porta **5432**
- Modo híbrido: scraper local tem melhor conectividade (seu ISP, não Railway IPs)
