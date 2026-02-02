#!/bin/bash
set -e

echo "🔄 Aguardando PostgreSQL ficar pronto..."
until pg_isready -h postgres -U postgres; do
  echo "⏳ PostgreSQL ainda não está pronto - aguardando..."
  sleep 2
done

echo "✅ PostgreSQL está pronto!"

echo "🏗️  Criando tabelas base..."
python -c "from models import Base, engine; Base.metadata.create_all(engine)"

echo "🔧 Aplicando migrações..."
PGPASSWORD=postgres123 psql -h postgres -U postgres -d betting_bot << 'EOF'
-- Adicionar colunas se não existirem
ALTER TABLE events ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP;
ALTER TABLE odds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE odds ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2);
ALTER TABLE odds ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2);

-- Atualizar valores padrão
UPDATE odds SET is_active = TRUE WHERE is_active IS NULL;

-- Criar índices se não existirem
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_odds_is_active ON odds(is_active);
CREATE INDEX IF NOT EXISTS idx_events_finished_at ON events(finished_at);
CREATE INDEX IF NOT EXISTS idx_odds_event_bookmaker ON odds(event_id, bookmaker);

-- Verificar status
SELECT 'Migrações aplicadas com sucesso!' as message;
EOF

echo "✅ Migrações aplicadas com sucesso!"

echo "🚀 Iniciando aplicação..."
exec "$@"
