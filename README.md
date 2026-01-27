# 🥛 LeiteBets - Bot de Arbitragem de Apostas

Sistema automatizado para identificar oportunidades de arbitragem em apostas esportivas usando Double Chance.

## 🎯 Funcionalidades

- ✅ API REST para receber odds de web scraper
- ✅ Cálculo automático de arbitragem com Double Chance
- ✅ Bot do Telegram com notificações em tempo real
- ✅ Suporte para múltiplas casas de apostas
- ✅ PostgreSQL via Docker

## 🛠️ Tecnologias

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Bot:** python-telegram-bot
- **Infra:** Docker

## 📦 Instalação

### Pré-requisitos
- Python 3.13+
- Docker
- Conta no Telegram

### Setup

1. Clone o repositório:
```bash
git clone https://github.com/MirandaLabs/leite-bets.git
cd leite-bets
```

2. Configure o ambiente:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Configure variáveis de ambiente (`.env`):
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres123@localhost:5432/betting_bot
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

4. Inicie o PostgreSQL:
```bash
docker-compose up -d
```

5. Execute o schema do banco:
```bash
docker exec -i betting-bot-db psql -U postgres -d betting_bot -c "ALTER TABLE odds ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2), ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2);"
```

6. Inicie o backend:
```bash
python main.py
```

7. Inicie o bot (outro terminal):
```bash
python telegram_bot.py
```

## 🔌 API Endpoints

### POST `/api/odds/update`
Recebe odds do web scraper.

**Request:**
```json
{
  "eventId": "evt_123",
  "sport": "Futebol",
  "league": "Brasileirão",
  "homeTeam": "Time A",
  "awayTeam": "Time B",
  "eventDate": "2026-01-28T20:00:00Z",
  "bookmaker": "Betano",
  "homeOdd": 2.10,
  "drawOdd": 3.20,
  "awayOdd": 3.50,
  "homeOrDrawOdd": 1.28,
  "awayOrDrawOdd": 1.82
}
```

## 🤖 Como funciona

1. Web scraper coleta odds de múltiplas casas
2. Odds são enviadas via API para o backend
3. Sistema calcula oportunidades de arbitragem usando Double Chance
4. Bot notifica o grupo do Telegram quando encontra oportunidades
5. Mensagens incluem cálculos detalhados e valores sugeridos

## 📊 Estrutura do Projeto
```
betting-bot/
├── backend/
│   ├── main.py          # API FastAPI
│   ├── models.py        # Modelos SQLAlchemy
│   ├── arbitrage.py     # Lógica de cálculo
│   ├── telegram_bot.py  # Bot do Telegram
│   ├── schema.sql       # Schema do banco
│   └── requirements.txt
└── docker-compose.yml   # PostgreSQL
```

## 🚀 Roadmap

- [ ] Versão V2 com N8N (fluxo conversacional)
- [ ] Dashboard web
- [ ] Suporte para mais mercados
- [ ] Histórico de oportunidades
- [ ] Notificações push

## 📝 Licença

MIT

## 👥 Autores

MirandaLabs