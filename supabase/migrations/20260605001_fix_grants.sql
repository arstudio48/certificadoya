-- ============================================================
-- FIX GRANTs - Restaurar permisos de anon para que RLS funcione
-- ============================================================
-- La migración 20260602002_fix_rls.sql revocó todos los permisos
-- de anon/public. Estas políticas RLS necesitan GRANTs explícitos.

GRANT INSERT ON leads TO anon;
GRANT SELECT ON leads TO anon;
GRANT INSERT ON newsletter_subscribers TO anon;
GRANT SELECT ON pisos TO anon;
GRANT SELECT ON tecnicos TO anon;
GRANT SELECT ON zonas_precio TO anon;
