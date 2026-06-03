-- Fix RLS on all Supabase tables
-- Triggered by Supabase Security Advisor alert (June 2026)
-- 6 tables lacked RLS, personal/financial data exposed to anon key

-- Enable RLS
ALTER TABLE blog_lectores ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_preguntas ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE transacciones_tecnicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_conversations ENABLE ROW LEVEL SECURITY;

-- Public-facing forms: anon INSERT only
DROP POLICY IF EXISTS "anon_insert_blog_lectores" ON blog_lectores;
CREATE POLICY "anon_insert_blog_lectores" ON blog_lectores FOR INSERT TO anon WITH CHECK (true);
DROP POLICY IF EXISTS "anon_insert_blog_preguntas" ON blog_preguntas;
CREATE POLICY "anon_insert_blog_preguntas" ON blog_preguntas FOR INSERT TO anon WITH CHECK (true);
DROP POLICY IF EXISTS "anon_insert_newsletter_subscribers" ON newsletter_subscribers;
CREATE POLICY "anon_insert_newsletter_subscribers" ON newsletter_subscribers FOR INSERT TO anon WITH CHECK (true);

-- Service role full access
DROP POLICY IF EXISTS "service_role_all_blog_lectores" ON blog_lectores;
CREATE POLICY "service_role_all_blog_lectores" ON blog_lectores FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "service_role_all_blog_preguntas" ON blog_preguntas;
CREATE POLICY "service_role_all_blog_preguntas" ON blog_preguntas FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "service_role_all_newsletter_subscribers" ON newsletter_subscribers;
CREATE POLICY "service_role_all_newsletter_subscribers" ON newsletter_subscribers FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "service_role_all_transacciones_tecnicos" ON transacciones_tecnicos;
CREATE POLICY "service_role_all_transacciones_tecnicos" ON transacciones_tecnicos FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "service_role_all_whatsapp_conversations" ON whatsapp_conversations;
CREATE POLICY "service_role_all_whatsapp_conversations" ON whatsapp_conversations FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "service_role_all_newsletter_history" ON newsletter_history;
CREATE POLICY "service_role_all_newsletter_history" ON newsletter_history FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Revoke default public access
REVOKE ALL ON blog_lectores FROM anon, public;
REVOKE ALL ON blog_preguntas FROM anon, public;
REVOKE ALL ON newsletter_subscribers FROM anon, public;
REVOKE ALL ON newsletter_history FROM anon, public;
REVOKE ALL ON transacciones_tecnicos FROM anon, public;
REVOKE ALL ON whatsapp_conversations FROM anon, public;
REVOKE ALL ON pageviews FROM anon, public;
REVOKE ALL ON leads FROM anon, public;
REVOKE ALL ON presupuestos FROM anon, public;
REVOKE ALL ON tecnicos FROM anon, public;
REVOKE ALL ON pisos FROM anon, public;
REVOKE ALL ON zonas_precio FROM anon, public;

-- Grant minimum required
GRANT INSERT ON blog_lectores TO anon;
GRANT INSERT ON blog_preguntas TO anon;
GRANT INSERT ON newsletter_subscribers TO anon;
GRANT INSERT ON pageviews TO anon;
GRANT SELECT ON pisos TO anon;
GRANT SELECT ON tecnicos TO anon;
GRANT SELECT ON zonas_precio TO anon;

GRANT ALL ON leads TO service_role;
GRANT ALL ON presupuestos TO service_role;
GRANT ALL ON transacciones_tecnicos TO service_role;
GRANT ALL ON whatsapp_conversations TO service_role;
GRANT ALL ON newsletter_history TO service_role;
GRANT ALL ON blog_lectores TO service_role;
GRANT ALL ON blog_preguntas TO service_role;
GRANT ALL ON newsletter_subscribers TO service_role;
