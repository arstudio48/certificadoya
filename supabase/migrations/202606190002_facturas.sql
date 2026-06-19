-- Migration: Facturas table + créditos inmobiliarias
-- Adds facturas table for billing all types, and transacciones_inmobiliarias for credit tracking

-- ============================================================
-- 1. Añadir columna saldo_creditos a inmobiliarias
-- ============================================================
ALTER TABLE inmobiliarias
  ADD COLUMN IF NOT EXISTS saldo_creditos INTEGER DEFAULT 0;

-- ============================================================
-- 2. Tabla de transacciones de créditos (inmobiliarias)
-- ============================================================
CREATE TABLE IF NOT EXISTS transacciones_inmobiliarias (
  id SERIAL PRIMARY KEY,
  inmobiliaria_id INTEGER NOT NULL REFERENCES inmobiliarias(id),
  tipo TEXT NOT NULL CHECK (tipo IN ('compra', 'gasto', 'ajuste')),
  cantidad INTEGER NOT NULL,
  concepto TEXT DEFAULT '',
  importe_euros DECIMAL(10,2) DEFAULT 0,
  saldo_resultante INTEGER NOT NULL,
  stripe_session_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. Tabla de facturas
-- ============================================================
CREATE TABLE IF NOT EXISTS facturas (
  id SERIAL PRIMARY KEY,
  num_factura TEXT NOT NULL UNIQUE,
  tipo TEXT NOT NULL CHECK (tipo IN ('cliente','tecnico','agencia')),
  emisor_nombre TEXT NOT NULL DEFAULT 'CertificadoYa',
  emisor_cif TEXT DEFAULT '',
  cliente_nombre TEXT NOT NULL,
  cliente_email TEXT,
  cliente_cif TEXT DEFAULT '',
  concepto TEXT NOT NULL,
  direccion TEXT DEFAULT '',
  base_imponible DECIMAL(10,2) NOT NULL,
  iva DECIMAL(10,2) NOT NULL DEFAULT 0,
  total DECIMAL(10,2) NOT NULL,
  lead_id INTEGER REFERENCES leads(id),
  tecnico_id INTEGER REFERENCES tecnicos(id),
  inmobiliaria_id INTEGER REFERENCES inmobiliarias(id),
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 4. Secuencia para numeración de facturas
-- ============================================================
CREATE SEQUENCE IF NOT EXISTS facturas_seq START 1;

-- Function to generate invoice number
CREATE OR REPLACE FUNCTION generar_num_factura()
RETURNS TEXT AS $$
DECLARE
  next_val INTEGER;
  year_str TEXT;
BEGIN
  next_val := nextval('facturas_seq');
  year_str := EXTRACT(YEAR FROM NOW())::TEXT;
  RETURN 'INV-' || year_str || '-' || LPAD(next_val::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;
