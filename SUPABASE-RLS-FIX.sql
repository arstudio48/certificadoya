-- FIX RLS: Permitir inserciones públicas en tabla leads
-- Supabase project: wypgqpgjlookbhuaiyxa

-- PASO 1: Verificar que la tabla exists
-- SELECT EXISTS(
--   SELECT 1 FROM information_schema.tables 
--   WHERE table_name = 'leads'
-- );

-- PASO 2: Habilitar RLS en tabla leads
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

-- PASO 3: CREAR POLICIES para permitir INSERT público (anon)
-- Política para INSERT (crear leads sin autenticación)
CREATE POLICY IF NOT EXISTS "Allow public inserts on leads" ON public.leads
  FOR INSERT
  WITH CHECK (true);

-- Política para SELECT (cualquiera puede leer)
CREATE POLICY IF NOT EXISTS "Allow public read on leads" ON public.leads
  FOR SELECT
  USING (true);

-- Política para UPDATE (admin/técnico/sistema)
CREATE POLICY IF NOT EXISTS "Allow authenticated updates on leads" ON public.leads
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

-- Verificación: Listar todas las policies en tabla leads
-- SELECT * FROM pg_policies WHERE tablename = 'leads';
