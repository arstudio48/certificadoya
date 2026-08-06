-- Migración: Añadir columna token para login OTP de inmobiliarias
-- Fecha: 19/06/2026

ALTER TABLE inmobiliarias
  ADD COLUMN IF NOT EXISTS token TEXT DEFAULT '',
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
