-- Migração para adicionar sistema de status de 3 estados
-- Execute este script para atualizar o banco de dados existente

-- 1. Adicionar coluna finished_at à tabela events (se não existir)
ALTER TABLE events 
ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP;

-- 2. Adicionar coluna is_active à tabela odds (se não existir)
ALTER TABLE odds 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 3. Atualizar valores is_active para odds existentes
UPDATE odds 
SET is_active = TRUE 
WHERE is_active IS NULL;

-- 4. Verificar e criar enum (para PostgreSQL)
-- Nota: Se usar outro banco (MySQL, SQLite), ajustar conforme necessário
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_status') THEN
        CREATE TYPE event_status AS ENUM ('upcoming', 'live', 'finished');
    END IF;
END $$;

-- 5. Garantir que status tenha valores válidos
UPDATE events 
SET status = 'upcoming' 
WHERE status NOT IN ('upcoming', 'live', 'finished');

-- 6. Criar índices para melhorar performance das consultas
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_odds_is_active ON odds(is_active);
CREATE INDEX IF NOT EXISTS idx_events_finished_at ON events(finished_at);

-- 7. Verificar eventos passados e atualizar status
-- Eventos que já deveriam estar finalizados (mais de 2 horas do horário)
UPDATE events 
SET status = 'finished', 
    finished_at = event_date + INTERVAL '2 hours'
WHERE status != 'finished' 
  AND event_date < (NOW() - INTERVAL '2 hours');

-- 8. Desativar odds de eventos finalizados
UPDATE odds 
SET is_active = FALSE 
WHERE event_id IN (
    SELECT id FROM events WHERE status = 'finished'
);

-- Verificação final
SELECT 
    status,
    COUNT(*) as count
FROM events
GROUP BY status
ORDER BY status;

SELECT 
    is_active,
    COUNT(*) as count
FROM odds
GROUP BY is_active;
