-- ============================================================
-- CERTIFICADOYA.ES — Esquema de Base de Datos (Supabase/PostgreSQL)
-- Versión: 1.0 — 20 Mayo 2026
-- ============================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TABLA: zonas_precio
-- Define el precio por m² según código postal
-- ============================================================
CREATE TABLE IF NOT EXISTS zonas_precio (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  provincia     TEXT NOT NULL,
  ciudad        TEXT,
  cp_inicio     TEXT NOT NULL,          -- Código postal inicio rango (ej: '33001')
  cp_fin        TEXT,                    -- Código postal fin rango (NULL = solo cp_inicio)
  precio_m2_min NUMERIC(6,2) NOT NULL,  -- Precio mínimo por m²
  precio_m2_max NUMERIC(6,2) NOT NULL,  -- Precio máximo por m²
  activo        BOOLEAN DEFAULT true,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para búsqueda rápida por código postal
CREATE INDEX IF NOT EXISTS idx_zonas_cp ON zonas_precio(cp_inicio, cp_fin);

-- ============================================================
-- TABLA: tecnicos
-- Técnicos certificadores registrados
-- ============================================================
CREATE TABLE IF NOT EXISTS tecnicos (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email           TEXT UNIQUE NOT NULL,
  nombre          TEXT NOT NULL,
  apellidos       TEXT,
  telefono        TEXT,
  titulacion      TEXT,                 -- 'arquitecto', 'aparejador', 'ingeniero'
  numero_colegiado TEXT,
  provincia       TEXT,                 -- Provincias donde opera (separadas por coma)
  cp_cobertura    TEXT[],               -- Array de códigos postales que cubre
  precio_m2       NUMERIC(6,2),         -- Su precio por m² (si lo fija)
  biografia       TEXT,
  verificado      BOOLEAN DEFAULT false,
  activo          BOOLEAN DEFAULT true,
  stripe_account  TEXT,                 -- ID cuenta Stripe Connect
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tecnicos_cp ON tecnicos USING GIN(cp_cobertura);
CREATE INDEX IF NOT EXISTS idx_tecnicos_activos ON tecnicos(activo) WHERE activo = true;

-- ============================================================
-- TABLA: leads
-- Solicitudes de presupuesto de clientes
-- ============================================================
CREATE TABLE IF NOT EXISTS leads (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nombre_cliente      TEXT NOT NULL,
  email_cliente       TEXT,
  telefono_cliente    TEXT,
  codigo_postal       TEXT NOT NULL,
  provincia           TEXT,
  ciudad              TEXT,
  direccion           TEXT,
  m2                  NUMERIC(7,2),     -- Metros cuadrados
  tipo_inmueble       TEXT,             -- 'piso', 'unifamiliar', 'adosado', 'local'
  antiguedad          TEXT,             -- 'menos de 10', '10-30', '30-50', 'más de 50', 'no sé'
  uso                 TEXT,             -- 'venta', 'alquiler', 'subvencion', 'otro'
  presupuesto_min     NUMERIC(6,2),     -- Presupuesto estimado mínimo
  presupuesto_max     NUMERIC(6,2),     -- Presupuesto estimado máximo
  tecnico_asignado    UUID REFERENCES tecnicos(id),
  estado              TEXT DEFAULT 'nuevo',  -- 'nuevo', 'asignado', 'contactado', 'presupuestado', 'completado', 'cancelado'
  notas               TEXT,
  fuente              TEXT DEFAULT 'web',   -- 'web', 'chatbot', 'whatsapp', 'gpt'
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_estado ON leads(estado);
CREATE INDEX IF NOT EXISTS idx_leads_cp ON leads(codigo_postal);
CREATE INDEX IF NOT EXISTS idx_leads_tecnico ON leads(tecnico_asignado);

-- ============================================================
-- TABLA: comisiones
-- Registro de comisiones por CEE completado
-- ============================================================
CREATE TABLE IF NOT EXISTS comisiones (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id       UUID REFERENCES leads(id) NOT NULL,
  tecnico_id    UUID REFERENCES tecnicos(id) NOT NULL,
  precio_final  NUMERIC(6,2),           -- Precio final que cobró el técnico
  comision_pct  NUMERIC(4,1) DEFAULT 18.0, -- Porcentaje de comisión
  comision_eur  NUMERIC(6,2),           -- Importe de la comisión en €
  pagada        BOOLEAN DEFAULT false,
  stripe_payment_id TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLA: valoraciones
-- Valoraciones de clientes a técnicos
-- ============================================================
CREATE TABLE IF NOT EXISTS valoraciones (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id     UUID REFERENCES leads(id) NOT NULL,
  tecnico_id  UUID REFERENCES tecnicos(id) NOT NULL,
  puntuacion  INTEGER CHECK (puntuacion BETWEEN 1 AND 5),
  comentario  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- FUNCIÓN: Calcular presupuesto estimado por CP
-- ============================================================
CREATE OR REPLACE FUNCTION calcular_presupuesto(
  p_cp TEXT,
  p_m2 NUMERIC
)
RETURNS TABLE (precio_min NUMERIC, precio_max NUMERIC)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT
    (zp.precio_m2_min * p_m2)::NUMERIC(6,2) AS precio_min,
    (zp.precio_m2_max * p_m2)::NUMERIC(6,2) AS precio_max
  FROM zonas_precio zp
  WHERE zp.activo = true
    AND zp.cp_inicio <= p_cp
    AND (zp.cp_fin IS NULL OR zp.cp_fin >= p_cp)
  ORDER BY zp.cp_inicio DESC
  LIMIT 1;
END;
$$;

-- ============================================================
-- DATOS INICIALES: Precios por zona (estimaciones conservadoras)
-- ============================================================
INSERT INTO zonas_precio (provincia, ciudad, cp_inicio, cp_fin, precio_m2_min, precio_m2_max) VALUES
  -- Madrid
  ('Madrid', 'Madrid', '28001', '28099', 0.75, 1.20),
  ('Madrid', 'Madrid periferia', '28100', '28999', 0.60, 0.95),
  -- Asturias
  ('Asturias', 'Gijón', '33201', '33213', 0.55, 0.90),
  ('Asturias', 'Oviedo', '33001', '33013', 0.55, 0.85),
  ('Asturias', 'Avilés', '33401', '33404', 0.50, 0.80),
  -- Barcelona
  ('Barcelona', 'Barcelona', '08001', '08099', 0.80, 1.30),
  ('Barcelona', 'Barcelona área metropolitana', '08100', '08999', 0.65, 1.00),
  -- Resto de España (por defecto)
  ('Nacional', NULL, '00001', '99999', 0.45, 0.85)
ON CONFLICT DO NOTHING;

-- ============================================================
-- POLÍTICAS RLS (Row Level Security)
-- ============================================================
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE tecnicos ENABLE ROW LEVEL SECURITY;

-- Leads: insert público (cualquiera puede enviar una solicitud)
CREATE POLICY "Permitir insert público en leads"
  ON leads FOR INSERT
  WITH CHECK (true);

-- Leads: solo el backoffice puede leer (usar API key)
CREATE POLICY "Backoffice puede leer leads"
  ON leads FOR SELECT
  USING (true);  -- Simplificado para MVP — luego se afina

-- Técnicos: pueden leer su propio perfil
CREATE POLICY "Técnico lee su perfil"
  ON tecnicos FOR SELECT
  USING (email = current_setting('request.jwt.claims', true)::json->>'email');

-- ============================================================
-- TABLA: whatsapp_conversations
-- Registro de conversaciones del bot de WhatsApp
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_conversations (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  wa_id          TEXT NOT NULL,           -- ID de WhatsApp del usuario
  nombre         TEXT,
  mensaje        TEXT NOT NULL,           -- Último mensaje
  respuesta       TEXT NOT NULL,          -- Respuesta del bot
  opcion         TEXT,                    -- Opción del menú seleccionada
  requiere_humano BOOLEAN DEFAULT false,  -- Si pidió hablar con persona
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wp_waid ON whatsapp_conversations(wa_id);
CREATE INDEX IF NOT EXISTS idx_wp_created ON whatsapp_conversations(created_at DESC);

