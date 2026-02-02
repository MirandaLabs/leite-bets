-- Criar database
CREATE DATABASE leite_bets;

-- Enum para status de eventos
CREATE TYPE event_status AS ENUM ('upcoming', 'live', 'finished');

-- Tabela de eventos (jogos)
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(50) PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    league VARCHAR(100) NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    event_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);

-- Tabela de odds
CREATE TABLE IF NOT EXISTS odds (
    id VARCHAR(50) PRIMARY KEY,
    event_id VARCHAR(50) REFERENCES events(id) ON DELETE CASCADE,
    bookmaker VARCHAR(50) NOT NULL,
    market VARCHAR(50) DEFAULT 'Resultado Final',
    home_odd DECIMAL(10, 2),
    draw_odd DECIMAL(10, 2),
    away_odd DECIMAL(10, 2),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_odds_event_bookmaker ON odds(event_id, bookmaker);

-- Tabela de oportunidades de arbitragem
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    id VARCHAR(50) PRIMARY KEY,
    event_id VARCHAR(50) REFERENCES events(id) ON DELETE CASCADE,
    user_bookmaker VARCHAR(50) NOT NULL,
    user_team VARCHAR(50) NOT NULL,
    user_odd DECIMAL(10, 2) NOT NULL,
    hedge_bookmaker VARCHAR(50) NOT NULL,
    hedge_team VARCHAR(50) NOT NULL,
    hedge_odd DECIMAL(10, 2) NOT NULL,
    profit_percent DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Tabela de requisições de usuários
CREATE TABLE IF NOT EXISTS user_requests (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    event_id VARCHAR(50) REFERENCES events(id) ON DELETE CASCADE,
    selected_team VARCHAR(50) NOT NULL,
    bookmaker VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_requests_user ON user_requests(user_id);