-- P6: Tablas para gestión de tasas CCAA dinámicas
-- Ejecutar en Supabase SQL Editor

-- Tabla: ccaa_tasas (maestro de tasas por CCAA)
CREATE TABLE IF NOT EXISTS ccaa_tasas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ccaa TEXT UNIQUE NOT NULL,
  codigo_provincia TEXT,
  tasa_euros NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
  tasa_porcentaje NUMERIC(5, 2) NOT NULL DEFAULT 0,
  base_obligatoria NUMERIC(8, 2) DEFAULT 65.55,  -- Actualizado +15% (28 jul 2026)
  decreto_referencia TEXT,
  vigencia_desde DATE NOT NULL DEFAULT CURRENT_DATE,
  vigencia_hasta DATE,
  activa BOOLEAN DEFAULT TRUE,
  notas TEXT,
  ultimo_actualizado TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: leads (actualizar con nuevos campos)
-- Si la tabla ya existe, ejecutar ALTER TABLE:
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS precio_base NUMERIC(8, 2) DEFAULT 65.55,  -- Actualizado +15% (28 jul 2026)
ADD COLUMN IF NOT EXISTS tasa_ccaa_provincia NUMERIC(8, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS tasa_debe_cobrar_ccaa BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tasa_estado TEXT DEFAULT 'pendiente' CHECK (tasa_estado IN ('pendiente', 'pagada_a_ccaa', 'rechazada')),
ADD COLUMN IF NOT EXISTS tasa_referencia_pago TEXT;

-- Tabla: audit_log (ya debería existir, pero aseguramos)
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  action TEXT NOT NULL,
  entity TEXT NOT NULL,
  entity_id UUID,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: pago_ccaa_registro (tracking de pagos a CCAA)
CREATE TABLE IF NOT EXISTS pago_ccaa_registro (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  ccaa TEXT NOT NULL,
  monto_pagado NUMERIC(8, 2) NOT NULL,
  numero_transaccion TEXT,
  numero_registro_cee TEXT,
  fecha_pago DATE NOT NULL DEFAULT CURRENT_DATE,
  metodo_pago TEXT, -- 'transferencia', 'api_ccaa', 'check', 'manual'
  estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'pagado', 'rechazado', 'devuelto')),
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insertar datos iniciales de tasas (28 julio 2026)
INSERT INTO ccaa_tasas (ccaa, codigo_provincia, tasa_euros, tasa_porcentaje, decreto_referencia, vigencia_desde, activa)
VALUES
  ('Asturias', '03', 12.00, 21.05, 'Decreto 5/2026', '2026-07-01', TRUE),
  ('Cantabria', '39', 8.50, 14.91, 'Orden 2026', '2026-06-15', TRUE),
  ('Cataluña', '08', 3.50, 6.14, 'Generalitat 2026', '2026-06-01', TRUE),
  ('Castilla y León', '05', 9.00, 15.79, 'Junta Castilla y León', '2026-03-01', TRUE),
  ('Galicia', '36', 10.00, 17.54, 'Resolución XUNTA 2026', '2026-05-01', TRUE),
  ('La Rioja', '26', 6.00, 10.53, 'Propuesta 2026', '2026-08-01', TRUE),
  ('Región de Murcia', '30', 5.00, 8.77, 'Regional CARM', '2026-07-15', TRUE),
  ('Navarra', '31', 7.50, 13.16, 'Foral Navarra 2026', '2026-04-01', TRUE),
  ('Madrid', '28', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Valencia', '46', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Andalucía', '41', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('País Vasco', '48', 0.00, 0.00, 'Foral (gratis)', '2026-01-01', TRUE),
  ('Baleares', '07', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Canarias', '35', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Extremadura', '06', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Aragón', '50', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Castilla-La Mancha', '13', 0.00, 0.00, 'N/A (gratis)', '2026-01-01', TRUE),
  ('Melilla', '52', 0.00, 0.00, 'Ciudad Autónoma', '2026-01-01', TRUE),
  ('Ceuta', '51', 0.00, 0.00, 'Ciudad Autónoma', '2026-01-01', TRUE)
ON CONFLICT (ccaa) DO UPDATE SET
  tasa_euros = EXCLUDED.tasa_euros,
  tasa_porcentaje = EXCLUDED.tasa_porcentaje,
  decreto_referencia = EXCLUDED.decreto_referencia,
  activa = EXCLUDED.activa,
  ultimo_actualizado = NOW();

-- Crear índices para performance
CREATE INDEX IF NOT EXISTS idx_ccaa_tasas_activa ON ccaa_tasas(activa) WHERE activa = TRUE;
CREATE INDEX IF NOT EXISTS idx_leads_tasa_estado ON leads(tasa_estado);
CREATE INDEX IF NOT EXISTS idx_leads_provincia_tasa ON leads(provincia, tasa_ccaa_provincia);
CREATE INDEX IF NOT EXISTS idx_pago_ccaa_registro_lead_id ON pago_ccaa_registro(lead_id);
CREATE INDEX IF NOT EXISTS idx_pago_ccaa_registro_estado ON pago_ccaa_registro(estado);

-- Crear vista: resumen de recaudación de tasas (query útil para reportes)
CREATE OR REPLACE VIEW v_resumen_tasas_mes AS
SELECT
  COALESCE(l.provincia, 'Desconocido') as provincia,
  COUNT(DISTINCT l.id) as leads_con_tasa,
  COALESCE(SUM(l.tasa_ccaa_provincia), 0) as total_recaudado,
  COALESCE(SUM(CASE WHEN l.tasa_estado = 'pagada_a_ccaa' THEN l.tasa_ccaa_provincia ELSE 0 END), 0) as ya_pagado,
  COALESCE(SUM(CASE WHEN l.tasa_estado = 'pendiente' THEN l.tasa_ccaa_provincia ELSE 0 END), 0) as pendiente_pagar,
  DATE_TRUNC('month', l.fecha_solicitud)::DATE as mes
FROM leads l
WHERE l.tasa_ccaa_provincia > 0
GROUP BY l.provincia, mes
ORDER BY mes DESC, total_recaudado DESC;

-- RLS Policy (seguridad): solo admin puede editar tasas
ALTER TABLE ccaa_tasas ENABLE ROW LEVEL SECURITY;
CREATE POLICY admin_only_ccaa_tasas ON ccaa_tasas
  FOR ALL USING (auth.role() = 'authenticated' AND auth.jwt()->>'role' = 'admin');

-- Crear función para actualizar timestamp
CREATE OR REPLACE FUNCTION actualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_pago_ccaa_updated_at
BEFORE UPDATE ON pago_ccaa_registro
FOR EACH ROW
EXECUTE FUNCTION actualizar_updated_at();
