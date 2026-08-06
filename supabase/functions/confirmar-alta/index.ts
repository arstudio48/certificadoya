// supabase/functions/confirmar-alta/index.ts
// Recibe el token del enlace y marca al técnico como confirmado.

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

serve(async (peticion) => {
  const url = new URL(peticion.url);
  const token = url.searchParams.get("token");

  if (!token || token.length < 32) {
    return new Response("Token inv\u00e1lido", { status: 400 });
  }

  const clienteSupabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  const { data, error } = await clienteSupabase
    .from("tecnicos_captacion")
    .update({ confirmado: true, confirmado_en: new Date().toISOString() })
    .eq("token_confirmacion", token)
    .eq("confirmado", false)
    .select("nombre, email")
    .maybeSingle();

  if (error || !data) {
    return Response.redirect("https://certificadoya.es/hazte-certificador/?estado=error", 302);
  }

  return Response.redirect("https://certificadoya.es/hazte-certificador/?estado=confirmado", 302);
});
