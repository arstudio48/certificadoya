-- Migración: Tabla inmobiliarias + columnas de seguimiento en leads y tecnicos
-- Fecha: 09/06/2026

-- ============================================================
-- 1. TABLA INMOBILIARIAS
-- ============================================================
CREATE TABLE IF NOT EXISTS inmobiliarias (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre TEXT NOT NULL,
  email TEXT,
  telefono TEXT,
  web TEXT,
  direccion TEXT,
  provincia TEXT,
  cif TEXT,
  contacto_nombre TEXT,
  notas TEXT,
  estado TEXT NOT NULL DEFAULT 'nuevo'
    CHECK (estado IN ('nuevo', 'contactado', 'interesado', 'cliente', 'rechazado', 'inactivo')),
  fuente TEXT DEFAULT 'foro'
    CHECK (fuente IN ('foro', 'web', 'recomendacion', 'scraping', 'manual', 'email')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ultimo_contacto TIMESTAMPTZ,
  proximo_paso TEXT,
  token_unsubscribe TEXT UNIQUE DEFAULT encode(gen_random_bytes(12), 'hex')
);

-- ============================================================
-- 2. COLUMNAS DE SEGUIMIENTO EN LEADS (propietarios)
-- ============================================================
ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS ultimo_contacto TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS proximo_paso TEXT,
  ADD COLUMN IF NOT EXISTS seguimiento_notas TEXT;

-- Añadir tipo a leads para distinguir propietario vs inmobiliaria legacy
ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS tipo TEXT DEFAULT 'propietario'
    CHECK (tipo IN ('propietario', 'inmobiliaria'));

-- ============================================================
-- 3. COLUMNAS DE SEGUIMIENTO EN TECNICOS
-- ============================================================
ALTER TABLE tecnicos
  ADD COLUMN IF NOT EXISTS ultimo_contacto TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS proximo_paso TEXT,
  ADD COLUMN IF NOT EXISTS seguimiento_notas TEXT;

-- ============================================================
-- 4. ÍNDICES PARA BÚSQUEDA RÁPIDA
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_inmobiliarias_provincia ON inmobiliarias(provincia);
CREATE INDEX IF NOT EXISTS idx_inmobiliarias_estado ON inmobiliarias(estado);
CREATE INDEX IF NOT EXISTS idx_leads_seguimiento_estado ON leads(estado);
CREATE INDEX IF NOT EXISTS idx_tecnicos_seguimiento_verificado ON tecnicos(verificado);

-- ============================================================
-- 5. RLS (Row Level Security)
-- ============================================================
ALTER TABLE inmobiliarias ENABLE ROW LEVEL SECURITY;

-- Anon: solo lectura
CREATE POLICY "anon_select_inmobiliarias"
  ON inmobiliarias FOR SELECT
  TO anon
  USING (true);

-- Anon: puede insertar (desde formulario web o agente)
CREATE POLICY "anon_insert_inmobiliarias"
  ON inmobiliarias FOR INSERT
  TO anon
  WITH CHECK (true);

-- Servicerole: todo
CREATE POLICY "service_all_inmobiliarias"
  ON inmobiliarias FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Grants
GRANT SELECT, INSERT ON inmobiliarias TO anon;
GRANT ALL ON inmobiliarias TO service_role;
GRANT USAGE ON SEQUENCE inmobiliarias_id_seq TO anon, service_role;

-- ============================================================
-- 6. FUNCIÓN: Estadísticas consolidadas de todos los leads
-- ============================================================
CREATE OR REPLACE FUNCTION get_seguimiento_stats()
RETURNS TABLE (
  tipo TEXT,
  total BIGINT,
  pendientes BIGINT,
  contactados BIGINT,
  interesados BIGINT,
  clientes BIGINT,
  hoy BIGINT,
  esta_semana BIGINT
) LANGUAGE SQL STABLE AS $$
-- Técnicos
SELECT 'tecnico'::TEXT, COUNT(*),
  COUNT(*) FILTER (WHERE verificado = false AND activo = true),
  COUNT(*) FILTER (WHERE verificado = true AND activo = true),
  0::BIGINT,
  0::BIGINT,
  COUNT(*) FILTER (WHERE created_at::DATE = CURRENT_DATE),
  COUNT(*) FILTER (WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE))
FROM tecnicos
UNION ALL
-- Propietarios (leads)
SELECT 'propietario'::TEXT, COUNT(*),
  COUNT(*) FILTER (WHERE estado IN ('nuevo','pendiente')),
  COUNT(*) FILTER (WHERE estado = 'pendiente'),
  0::BIGINT,
  COUNT(*) FILTER (WHERE estado = 'asignado'),
  COUNT(*) FILTER (WHERE created_at::DATE = CURRENT_DATE),
  COUNT(*) FILTER (WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE))
FROM leads
UNION ALL
-- Inmobiliarias
SELECT 'inmobiliaria'::TEXT, COUNT(*),
  COUNT(*) FILTER (WHERE estado = 'nuevo'),
  COUNT(*) FILTER (WHERE estado = 'contactado'),
  COUNT(*) FILTER (WHERE estado = 'interesado'),
  COUNT(*) FILTER (WHERE estado = 'cliente'),
  COUNT(*) FILTER (WHERE created_at::DATE = CURRENT_DATE),
  COUNT(*) FILTER (WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE))
FROM inmobiliarias;
$$;

-- ============================================================
-- 7. ACTUALIZAR LEADS EXISTENTES (añadir tipo)
-- ============================================================
UPDATE leads SET tipo = 'propietario' WHERE tipo IS NULL;
