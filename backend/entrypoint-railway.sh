#!/bin/bash
set -e

echo "🔄 Configuração Railway..."

# Railway fornece DATABASE_URL automaticamente
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não encontrada!"
    exit 1
fi

echo "✅ DATABASE_URL configurada"

# Extrai credenciais do DATABASE_URL para psql
# Formato: postgresql://user:pass@host:port/db
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

echo "📡 Aguardando PostgreSQL ficar pronto..."
until PGPASSWORD=$DB_PASS pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
  echo "⏳ PostgreSQL ainda não está pronto - aguardando..."
  sleep 2
done

echo "✅ PostgreSQL está pronto!"

echo "🗃️ Criando tabelas base..."
python -c "from models import Base, engine; Base.metadata.create_all(engine)"

echo "🔧 Aplicando migrações..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
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

SELECT 'Migrações aplicadas com sucesso!' as message;
EOF

echo "✅ Migrações aplicadas!"

echo "🚀 Iniciando API..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}