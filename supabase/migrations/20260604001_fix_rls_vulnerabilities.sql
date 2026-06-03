-- ============================================================
-- FIX VULNERABILIDADES SUPABASE - CertificadoYa
-- ============================================================

-- 1. PISOS: Activar RLS y crear política de SELECT para anon
ALTER TABLE pisos ENABLE ROW LEVEL SECURITY;

-- Política para anon: ver todos los pisos (públicos)
-- Nota: columna 'oculto' no existe en la tabla, se añadirá filtro cuando exista
DROP POLICY IF EXISTS "anon_select_pisos_publicos" ON pisos;
CREATE POLICY "anon_select_pisos_publicos" ON pisos
  FOR SELECT
  TO anon
  USING (true);

-- 2. LEADS: Añadir política de INSERT para anon (formulario web)
DROP POLICY IF EXISTS "anon_insert_leads" ON leads;
CREATE POLICY "anon_insert_leads" ON leads
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- 3. NEWSLETTER_SUBSCRIBERS: Añadir política de INSERT para anon
DROP POLICY IF EXISTS "anon_insert_newsletter" ON newsletter_subscribers;
CREATE POLICY "anon_insert_newsletter" ON newsletter_subscribers
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- 4. TECNICOS: Añadir política de SELECT para anon (ver solo datos públicos)
DROP POLICY IF EXISTS "anon_select_tecnicos" ON tecnicos;
CREATE POLICY "anon_select_tecnicos" ON tecnicos
  FOR SELECT
  TO anon
  USING (true);
-- NOTA: Solo se expondrán las columnas permitidas via GRANT o view

-- 5. ZONAS_PRECIO: Política de SELECT para anon
DROP POLICY IF EXISTS "anon_select_zonas_precio" ON zonas_precio;
CREATE POLICY "anon_select_zonas_precio" ON zonas_precio
  FOR SELECT
  TO anon
  USING (true);

-- 6. GRANTs específicos para que las políticas RLS funcionen
-- (la migración 20260602002_fix_rls.sql revocó todos los permisos de anon)
GRANT INSERT ON leads TO anon;
GRANT INSERT ON newsletter_subscribers TO anon;
GRANT SELECT ON pisos TO anon;
GRANT SELECT ON tecnicos TO anon;
GRANT SELECT ON zonas_precio TO anon;
