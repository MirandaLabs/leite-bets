-- Script de atualização incremental do schema do banco de dados
-- Adiciona novas colunas e índices conforme evolução do projeto

-- 1. Adicionar colunas de Double Chance (se não existirem)
ALTER TABLE odds 
ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2);

-- 2. Adicionar coluna de mercado (se não existir)
ALTER TABLE odds 
ADD COLUMN IF NOT EXISTS market VARCHAR(50) DEFAULT 'Resultado Final';

-- 3. Adicionar sistema de status de 3 estados
ALTER TABLE events 
ADD COLUMN IF NOT EXISTS finished_at TIMESTAMP;

ALTER TABLE odds 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 4. Atualizar valores is_active para odds existentes
UPDATE odds 
SET is_active = TRUE 
WHERE is_active IS NULL;

-- 5. Garantir que status tenha valores válidos
UPDATE events 
SET status = 'upcoming' 
WHERE status NOT IN ('upcoming', 'live', 'finished');

-- 6. Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_odds_event_bookmaker ON odds(event_id, bookmaker);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_odds_is_active ON odds(is_active);
CREATE INDEX IF NOT EXISTS idx_events_finished_at ON events(finished_at);

-- 7. Atualizar eventos passados para finished
UPDATE events 
SET status = 'finished', 
    finished_at = event_date + INTERVAL '2 hours'
WHERE status != 'finished' 
  AND event_date < (NOW() - INTERVAL '2 hours');

-- 8. Desativar odds de eventos finalizados
UPDATE odds 
SET is_active = FALSE 
WHERE event_id IN (SELECT id FROM events WHERE status = 'finished');

-- Verificação final
SELECT 'Schema atualizado com sucesso!' as message;

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'odds';