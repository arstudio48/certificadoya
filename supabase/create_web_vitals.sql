CREATE TABLE IF NOT EXISTS web_vitals (
  id BIGSERIAL PRIMARY KEY,
  metric_name TEXT NOT NULL,
  value NUMERIC NOT NULL,
  rating TEXT NOT NULL,
  delta NUMERIC,
  metric_id TEXT,
  url TEXT,
  referrer TEXT,
  received_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_web_vitals_metric ON web_vitals(metric_name);
CREATE INDEX IF NOT EXISTS idx_web_vitals_date ON web_vitals(received_at);
