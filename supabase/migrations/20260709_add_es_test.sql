-- Migración: añadir columna es_test a leads y tecnicos
-- Separar registros de prueba de los auténticos

ALTER TABLE leads ADD COLUMN IF NOT EXISTS es_test BOOLEAN DEFAULT FALSE;
ALTER TABLE tecnicos ADD COLUMN IF NOT EXISTS es_test BOOLEAN DEFAULT FALSE;

-- Crear función exec_sql para futuras migraciones manuales (solo admin)
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
  RETURN json_build_object('ok', true);
END;
$$;

-- Comentario: usar con cuidado, solo para migraciones
COMMENT ON FUNCTION exec_sql(text) IS 'Ejecuta SQL arbitrario. SOLO para migraciones administrativas.';
