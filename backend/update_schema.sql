ALTER TABLE odds 
ADD COLUMN IF NOT EXISTS home_or_draw_odd DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS away_or_draw_odd DECIMAL(10, 2);


SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'odds';