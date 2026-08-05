import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_ROLE_KEY = Deno.env.get("SERVICE_ROLE_KEY") ?? "";
const SUPABASE_URL_EXT = "https://wypgqpgjlookbhuaiyxa.supabase.co";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

/**
 * REGLA: si un técnico tiene un lead asignado y no hace uso del lead en 72 horas,
 * se pasa al técnico más nuevo de esa zona (provincia).
 *
 * "Hacer uso" = enviar al menos 1 mensaje en el chat (mensajes_encargo.de_tecnico=true)
 * o cambiar el estado del lead a algo que no sea 'asignado'/'pendiente_tecnico'.
 */
const HORAS_INACTIVIDAD = 72;

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  try {
    const cutoff = new Date(Date.now() - HORAS_INACTIVIDAD * 3600 * 1000).toISOString();

    // 1. Leads asignados hace >72h, sin actividad del técnico
    const { data: leadsInactivos, error: qErr } = await supabase
      .from("leads")
      .select("id, nombre_cliente, email_cliente, provincia, estado, tecnico_asignado, fecha_asignacion")
      .not("tecnico_asignado", "is", null)
      .not("stripe_payment_intent", "is", null) // solo leads con pago
      .lte("fecha_asignacion", cutoff)
      .in("estado", ["asignado", "pendiente_tecnico"]);

    if (qErr || !leadsInactivos || leadsInactivos.length === 0) {
      return new Response(
        JSON.stringify({ success: true, message: "Sin leads inactivos para reasignar", reasignados: 0 }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const reasignados: string[] = [];

    for (const lead of leadsInactivos) {
      // 2. Verificar que no haya actividad del técnico en el chat
      const { data: msgs } = await supabase
        .from("mensajes_encargo")
        .select("id")
        .eq("encargo_id", lead.id)
        .eq("de_tecnico", true)
        .gt("created_at", lead.fecha_asignacion)
        .limit(1);

      if (msgs && msgs.length > 0) continue; // el técnico sí habló, skip

      // 3. Buscar técnico más nuevo de la provincia (excluyendo el actual y el dueño)
      const EXCLUIR_PERMANENTE = ["4b805c7b-0bbf-490d-8000-21c620cbf30f"];
      const provNorm = (lead.provincia || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

      const { data: tecnicos } = await supabase
        .from("tecnicos")
        .select("id, nombre, email, provincia, created_at")
        .eq("activo", true)
        .eq("verificado", true)
        .not("id", "in", `(${EXCLUIR_PERMANENTE.join(",")},${lead.tecnico_asignado})`);

      if (!tecnicos || tecnicos.length === 0) continue;

      // Filtrar por provincia (normalizada, incluyendo limítrofes si hace falta)
      const candidatos = tecnicos.filter((t) => {
        const provinciasTecnico = String(t.provincia || "").split(",").map((x) =>
          x.trim().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
        );
        return provinciasTecnico.some((p) => p === provNorm);
      });

      if (candidatos.length === 0) continue;

      // El más nuevo = el que se registró más recientemente
      const masNuevo = candidatos.sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )[0];

      // 4. Reasignar
      const nombreTecnicoViejo = lead.tecnico_asignado;
      await supabase
        .from("leads")
        .update({
          tecnico_asignado: masNuevo.id,
          estado: "pendiente_tecnico",
          fecha_asignacion: new Date().toISOString(),
          notas: `Reasignado de ${nombreTecnicoViejo} (72h sin actividad) → ${masNuevo.nombre}`,
        })
        .eq("id", lead.id);

      // 5. Notificar al nuevo técnico
      const chatUrl = `${SUPABASE_URL_EXT}/chat.html?encargo=${lead.id}`;
      const WEB = "https://www.certificadoya.es";
      const panelUrl = `${WEB}/panel-tecnico.html?token=${masNuevo.email || ""}`;

      await fetch(`${SUPABASE_URL_EXT}/functions/v1/enviar-correo`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${SERVICE_ROLE_KEY}` },
        body: JSON.stringify({
          to: masNuevo.email,
          subject: `🔄 Encargo reasignado en ${lead.provincia || ""} — CertificadoYa`,
          html: `
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:20px">
              <div style="background:#fff;border-radius:12px;padding:30px">
                <h1 style="color:#16a34a;font-size:22px">🔄 Encargo reasignado</h1>
                <p>Hola <strong>${masNuevo.nombre}</strong>,</p>
                <p>Un técnico anterior no respondió en 72 horas. El encargo en <strong>${lead.provincia || ""}</strong> ahora es tuyo.</p>
                <table style="width:100%;border-collapse:collapse;margin:15px 0">
                  <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Cliente</td><td style="padding:8px;border-bottom:1px solid #eee">${lead.nombre_cliente || ""}</td></tr>
                  <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Zona</td><td style="padding:8px;border-bottom:1px solid #eee">${lead.provincia || ""}</td></tr>
                </table>
                <p style="margin-top:20px"><a href="${chatUrl}" style="background:#16a34a;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block">💬 Contactar al cliente (chat)</a></p>
                <p style="color:#888;font-size:12px;margin-top:15px">El cliente ya pagó. Tienes 72 horas para contactar o se reasignará automáticamente.</p>
              </div>
            </div>`,
        }),
      });

      reasignados.push(`${lead.nombre_cliente} → ${masNuevo.nombre}`);
    }

    return new Response(
      JSON.stringify({
        success: true,
        reasignados: reasignados.length,
        detalle: reasignados,
        mensaje: reasignados.length > 0
          ? `${reasignados.length} lead(s) reasignado(s) a técnico(s) más nuevo(s)`
          : "Sin leads inactivos que reasignar",
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ success: false, error: err.message }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
