CREATE OR REPLACE FUNCTION incrementar_visita(piso_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.pisos SET visitas = visitas + 1 WHERE id = piso_id;
END;
$$;
