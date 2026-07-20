-- Añadir campos de FP y módulos RD 659/2025 a la tabla tecnicos
-- Propósito: identificar técnicos de Formación Profesional (CFGS/FP) para
-- actuar según el RD 659/2025 (vigor final de mes / cuando noticias lo indiquen).
-- Estos técnicos NO reciben clientes hasta que puedan ejercer legalmente.

ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS es_fp BOOLEAN DEFAULT FALSE;
ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS modulos_rd659 TEXT DEFAULT '';
ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS puede_ejercer BOOLEAN DEFAULT FALSE;
ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS nota_fp TEXT DEFAULT '';

COMMENT ON COLUMN tecnicos.es_fp IS 'TRUE si el técnico es FP/CFGS (no titulación LOE)';
COMMENT ON COLUMN tecnicos.modulos_rd659 IS 'Módulos 1/2 completados según RD 659/2025';
COMMENT ON COLUMN tecnicos.puede_ejercer IS 'FALSE hasta que el RD 659/2025 esté vigente y pueda firmar CEE';
COMMENT ON COLUMN tecnicos.nota_fp IS 'Notas sobre situación FP del técnico';
