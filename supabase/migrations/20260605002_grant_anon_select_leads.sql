-- ============================================================
-- Fix: Grant SELECT on leads to anon role
-- ============================================================
-- La migración 20260605001_fix_grants.sql incluía INSERT pero
-- no SELECT en leads. El script notificar-leads.py usa ANON_KEY
-- para hacer SELECT vía REST API y necesita este permiso.

GRANT SELECT ON public.leads TO anon;
