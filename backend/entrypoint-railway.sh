#!/bin/bash
set -e

echo "🔄 Configuração Railway..."

# Railway fornece DATABASE_URL automaticamente
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não encontrada!"
    exit 1
fi

echo "✅ DATABASE_URL configurada"

# No Railway, o PostgreSQL já está disponível via DATABASE_URL
# Não precisa fazer pg_isready porque SQLAlchemy faz retry automaticamente

echo "🗃️ Criando tabelas base..."
python -c "from models import Base, engine; Base.metadata.create_all(engine)" || {
    echo "⚠️  Erro ao criar tabelas, mas continuando..."
}

echo "🔧 Aplicando migrações via Python..."
python << 'PYTHON_SCRIPT'
from models import engine

migrations = """
ALTER TABLE events ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP;
ALTER TABLE odds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE odds ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2);
ALTER TABLE odds ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2);
UPDATE odds SET is_active = TRUE WHERE is_active IS NULL;
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_odds_is_active ON odds(is_active);
CREATE INDEX IF NOT EXISTS idx_events_finished_at ON events(finished_at);
CREATE INDEX IF NOT EXISTS idx_odds_event_bookmaker ON odds(event_id, bookmaker);
"""

with engine.connect() as conn:
    for statement in migrations.strip().split(';'):
        if statement.strip():
            try:
                conn.execute(statement)
                conn.commit()
            except Exception as e:
                print(f'Migration skipped: {e}')

print('✅ Migrações aplicadas!')
PYTHON_SCRIPT

echo "🚀 Iniciando API..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}