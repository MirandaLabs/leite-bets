#!/usr/bin/env python3
"""
Script de inicialização para Railway
Garante que o banco está acessível antes de iniciar o servidor
"""
import os
import sys
import time
from sqlalchemy import create_engine, text

def wait_for_db(max_retries=30, delay=2):
    """Aguarda o PostgreSQL ficar disponível"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não configurada!")
        sys.exit(1)
    
    # Garante que usa psycopg3 (não psycopg2)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    print(f"🔄 Verificando conexão com PostgreSQL...")
    
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ PostgreSQL conectado! (tentativa {attempt})")
            return engine
        except Exception as e:
            print(f"⏳ Tentativa {attempt}/{max_retries} - PostgreSQL não disponível: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                print("❌ Timeout esperando PostgreSQL!")
                sys.exit(1)

def create_tables(engine):
    """Cria as tabelas do banco"""
    try:
        print("🗃️  Criando tabelas...")
        from models import Base
        Base.metadata.create_all(engine)
        print("✅ Tabelas criadas!")
    except Exception as e:
        print(f"⚠️  Erro ao criar tabelas: {e}")
        # Não faz exit porque as tabelas podem já existir

def run_migrations(engine):
    """Executa migrações SQL"""
    migrations = [
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP",
        "ALTER TABLE odds ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
        "ALTER TABLE odds ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2)",
        "ALTER TABLE odds ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2)",
        "UPDATE odds SET is_active = TRUE WHERE is_active IS NULL",
        "CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)",
        "CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date)",
        "CREATE INDEX IF NOT EXISTS idx_odds_is_active ON odds(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_events_finished_at ON events(finished_at)",
        "CREATE INDEX IF NOT EXISTS idx_odds_event_bookmaker ON odds(event_id, bookmaker)",
    ]
    
    try:
        print("🔧 Executando migrações...")
        with engine.connect() as conn:
            for migration in migrations:
                try:
                    conn.execute(text(migration))
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Migration skipped: {str(e)[:50]}")
        print("✅ Migrações aplicadas!")
    except Exception as e:
        print(f"⚠️  Erro nas migrações: {e}")

def start_server():
    """Inicia o servidor uvicorn"""
    import uvicorn
    
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Iniciando servidor na porta {port}...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    print("=" * 60)
    print("🔵 RAILWAY STARTUP SCRIPT")
    print("=" * 60)
    
    # 1. Aguardar PostgreSQL
    engine = wait_for_db()
    
    # 2. Criar tabelas
    create_tables(engine)
    
    # 3. Executar migrações
    run_migrations(engine)
    
    # 4. Iniciar servidor
    print("=" * 60)
    start_server()
