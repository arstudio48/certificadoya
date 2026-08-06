-- Trigger para notificar automáticamente al insertar un lead
-- Llama a la Edge Function notificar-lead via pg_net

CREATE OR REPLACE FUNCTION public.notificar_nuevo_lead()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  PERFORM
    net.http_post(
      url := 'https://wypgqpgjlookbhuaiyxa.supabase.co/functions/v1/notificar-lead',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object(
        'type', 'INSERT',
        'table', 'leads',
        'schema', 'public',
        'record', row_to_json(NEW)
      )::text
    );
  RETURN NEW;
END;
$$;

-- Eliminar trigger si existe
DROP TRIGGER IF EXISTS tr_notificar_nuevo_lead ON public.leads;

-- Crear el trigger
CREATE TRIGGER tr_notificar_nuevo_lead
  AFTER INSERT ON public.leads
  FOR EACH ROW
  EXECUTE FUNCTION public.notificar_nuevo_lead();
