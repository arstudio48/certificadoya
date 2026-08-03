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
 * Busca el siguiente técnico disponible para una provincia,
 * excluyendo los que ya rechazaron este lead.
 */
async function buscarTecnicoDisponible(
  provincia: string,
  leadId: string,
  excluir: string[] = [],
): Promise<string | null> {
  // Exclusión permanente: el dueño (arturo) nunca recibe encargos asignados automáticamente
  const EXCLUIR_PERMANENTE = ["4b805c7b-0bbf-490d-8000-21c620cbf30f"];
  const excluirTotal = [...new Set([...excluir, ...EXCLUIR_PERMANENTE])];

  // Técnicos de la provincia, activos y verificados
  const { data: tecnicos } = await supabase
    .from("tecnicos")
    .select("id, nombre, email, modelo_pago, saldo_creditos, premium_hasta, verificado, activo")
    .eq("activo", true)
    .eq("verificado", true)
    .ilike("provincia", `%${provincia}%`);

  if (!tecnicos || tecnicos.length === 0) return null;

  const candidatos = tecnicos.filter((t) => {
    if (excluirTotal.includes(t.id)) return false;
    if (t.modelo_pago === "premium") {
      // premium_hasta NULL = permanente (válido); si tiene fecha, debe ser futura
      return !t.premium_hasta || new Date(t.premium_hasta) > new Date();
    }
    return (t.saldo_creditos ?? 0) >= 1;
  });

  const ordenados = candidatos
    .sort((a, b) => {
      const aPrem = a.modelo_pago === "premium" ? 1 : 0;
      const bPrem = b.modelo_pago === "premium" ? 1 : 0;
      if (aPrem !== bPrem) return bPrem - aPrem;
      return (b.saldo_creditos ?? 0) - (a.saldo_creditos ?? 0);
    });

  return ordenados.length > 0 ? ordenados[0].id : null;
}

/**
 * Notifica al técnico asignado.
 * - Primeros 3 leads: email con datos completos del lead + instrucciones de onboarding.
 * - Del 4º en adelante: email breve con enlace a la página desindexada (panel-tecnico.html?token=).
 * Incrementa el contador leads_recibidos del técnico.
 */
async function notificarAsignacion(leadId: string, tecnicoId: string) {
  const { data: lead } = await supabase
    .from("leads")
    .select("id, nombre_cliente, email_cliente, telefono_cliente, codigo_postal, provincia, m2, tipo_inmueble")
    .eq("id", leadId)
    .maybeSingle();

  const { data: tecnico } = await supabase
    .from("tecnicos")
    .select("id, nombre, email, token, leads_recibidos")
    .eq("id", tecnicoId)
    .maybeSingle();

  if (!lead || !tecnico?.email) return;

  // Incrementar contador de leads recibidos
  const recibidos = (tecnico.leads_recibidos ?? 0) + 1;
  await supabase.from("tecnicos").update({ leads_recibidos: recibidos }).eq("id", tecnicoId);

  const WEB = "https://www.certificadoya.es";
  const panelUrl = `${WEB}/panel-tecnico.html?token=${tecnico.token ?? ""}`;
  const esPrimeros = recibidos <= 3;

  let html: string;
  let subject: string;

  if (esPrimeros) {
    // Email completo con datos del lead + instrucciones de onboarding
    subject = `📋 Nuevo encargo en ${lead.provincia || lead.codigo_postal} — CertificadoYa (${recibidos}/3)`;
    html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #16a34a;">📋 Nuevo encargo asignado</h2>
      <p>Hola <strong>${tecnico.nombre}</strong>, tienes un nuevo encargo en <strong>${lead.provincia || lead.codigo_postal}</strong>:</p>
      <table style="width: 100%; border-collapse: collapse;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Cliente</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.nombre_cliente}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="tel:${lead.telefono_cliente}">${lead.telefono_cliente}</a></td></tr>
        ${lead.email_cliente ? `<tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.email_cliente}</td></tr>` : ""}
        ${lead.m2 ? `<tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.m2} m²${lead.tipo_inmueble ? " - " + lead.tipo_inmueble : ""}</td></tr>` : ""}
      </table>
      <div style="background:#f2f8f4; border-radius:12px; padding:18px 20px; margin:18px 0; font-size:14px; line-height:1.7; color:#1a2b23;">
        <strong style="color:#0f6b3d;">Cómo funciona CertificadoYa:</strong><br>
        1. <strong>Contactas al cliente</strong> por teléfono/WhatsApp para acordar la visita.<br>
        2. <strong>Haces la visita y emites el CEE</strong> como siempre (tú eres el técnico colegiado).<br>
        3. <strong>El cliente ya pagó</strong> — el cobro está retenido de forma segura.<br>
        4. <strong>Cobras tú</strong> al completar el encargo (comisión 18% que restamos). Pago vía Stripe o transferencia.<br>
        5. Subes el certificado y nosotros gestionamos el registro oficial.
      </div>
      <p style="margin-top: 20px;"><a href="${panelUrl}" style="background:#16a34a;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;">Ver mis encargos en el panel</a></p>
      <p style="color:#888;font-size:12px;">Este es el encargo nº ${recibidos} de tus 3 primeros. A partir del 4º, te avisaremos con un enlace a tu panel (sin datos en el email) para tu comodidad.</p>
    </div>`;
  } else {
    // Email breve con enlace a página desindexada (sin datos del lead)
    subject = `📋 Tienes un nuevo encargo en CertificadoYa — míralo en tu panel`;
    html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #16a34a;">📋 Nuevo encargo disponible</h2>
      <p>Hola <strong>${tecnico.nombre}</strong>, tienes un nuevo encargo asignado en <strong>${lead.provincia || lead.codigo_postal}</strong>.</p>
      <p>Por privacidad y comodidad, los datos del cliente están en tu panel privado (no indexable):</p>
      <p style="margin-top: 20px;"><a href="${panelUrl}" style="background:#16a34a;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;">Abrir mi panel de encargos →</a></p>
      <p style="color:#888;font-size:12px;">Recordatorio: contactas al cliente, emites el CEE, y cobras al completar (comisión 18%). El cliente ya pagó y el importe está retenido.</p>
    </div>`;
  }

  await fetch(SUPABASE_URL_EXT + "/functions/v1/enviar-correo", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + SERVICE_ROLE_KEY },
    body: JSON.stringify({
      to: tecnico.email,
      subject,
      html,
    }),
  });

  // Confirmación al cliente (ya la hizo notificar-lead, pero aseguramos)
  if (lead.email_cliente) {
    await fetch(SUPABASE_URL_EXT + "/functions/v1/notificar-lead", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + SERVICE_ROLE_KEY },
      body: JSON.stringify(lead),
    });
  }
}

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  try {
    const body = await req.json();
    const { leadId, excluir = [] } = body;

    if (!leadId) {
      return new Response(JSON.stringify({ error: "leadId requerido" }), { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Obtener lead
    const { data: lead, error: leadErr } = await supabase
      .from("leads")
      .select("id, nombre_cliente, provincia, estado, tecnico_asignado")
      .eq("id", leadId)
      .maybeSingle();

    if (leadErr || !lead) {
      return new Response(JSON.stringify({ error: "Lead no encontrado" }), { status: 404, headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Si ya tiene técnico asignado, no hacer nada (aunque el estado sea pendiente_tecnico)
    if (lead.tecnico_asignado) {
      return new Response(JSON.stringify({ success: true, message: "Ya asignado", tecnico_id: lead.tecnico_asignado }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Si ya está asignado y aceptado, no hacer nada
    if (lead.estado === "asignado" || lead.estado === "pagado" || lead.estado === "completado") {
      return new Response(JSON.stringify({ success: true, message: "Ya asignado", tecnico_id: lead.tecnico_asignado }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    const tecnicoId = await buscarTecnicoDisponible(lead.provincia || "", leadId, excluir);

    if (!tecnicoId) {
      // No hay técnico disponible en la provincia → dejar pendiente para reintento
      await supabase.from("leads").update({ estado: "pendiente" }).eq("id", leadId);
      return new Response(JSON.stringify({ success: false, message: "Sin técnico disponible en la zona", reintentar: true }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Asignar
    const now = new Date().toISOString();
    const { error: updErr } = await supabase
      .from("leads")
      .update({ estado: "pendiente_tecnico", tecnico_asignado: tecnicoId, fecha_asignacion: now })
      .eq("id", leadId);

    if (updErr) {
      return new Response(JSON.stringify({ error: updErr.message }), { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Notificar
    await notificarAsignacion(leadId, tecnicoId);

    return new Response(JSON.stringify({ success: true, tecnico_id: tecnicoId, message: "Asignado automáticamente" }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
  } catch (err) {
    return new Response(JSON.stringify({ success: false, error: err.message }), { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }
});
