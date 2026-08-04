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
 * Mapa de provincias liminales del fallback.
 * Clave = provincia normalizada del lead (minúsculas, sin tildes).
 * Valor = provincias cotindantes donde buscar técnico si no hay en la exacta.
 */
const PROVINCIAS_LIMITROFES: Record<string, string[]> = {
  "madrid": ["guadalajara", "toledo", "avila", "segovia", "cuenca"],
  "ciudad real": ["toledo", "albacete", "badajoz", "jaen", "cordoba", "cuenca"],
  "zamora": ["leon", "valladolid", "salamanca", "ourense"],
  "barcelona": ["tarragona", "lleida", "girona"],
  "valencia": ["castellon", "teruel", "albacete", "alicante", "cuenca"],
  "alicante": ["valencia", "albacete", "murcia"],
  "murcia": ["alicante", "almeria", "albacete", "granada", "jaen"],
  "asturias": ["leon", "lugo", "cantabria"],
  "leon": ["asturias", "palencia", "valladolid", "zamora", "ourense", "lugo"],
  "cantabria": ["asturias", "leon", "palencia", "burgos", "bizkaia"],
  "burgos": ["palencia", "valladolid", "segovia", "soria", "la rioja", "alava", "bizkaia", "cantabria"],
  "salamanca": ["zamora", "valladolid", "avila", "caceres"],
  "valladolid": ["zamora", "leon", "palencia", "burgos", "segovia", "avila", "salamanca"],
  "girona": ["barcelona", "lleida"],
  "tarragona": ["barcelona", "lleida", "castellon", "teruel"],
  "lleida": ["barcelona", "girona", "tarragona", "huesca", "zaragoza"],
  "huesca": ["zaragoza", "lleida", "navarra"],
  "zaragoza": ["huesca", "navarra", "la rioja", "soria", "guadalajara", "teruel", "lleida"],
  "teruel": ["zaragoza", "guadalajara", "cuenca", "valencia", "tarragona", "castellon"],
  "cuenca": ["guadalajara", "madrid", "toledo", "ciudad real", "albacete", "valencia", "teruel"],
  "guadalajara": ["madrid", "cuenca", "segovia", "soria", "zaragoza"],
  "albacete": ["cuenca", "valencia", "alicante", "murcia", "jaen", "ciudad real"],
  "jaen": ["ciudad real", "albacete", "murcia", "granada", "cordoba"],
  "granada": ["almeria", "murcia", "jaen", "cordoba", "malaga"],
  "cordoba": ["sevilla", "malaga", "jaen", "ciudad real", "badajoz"],
  "almeria": ["murcia", "granada"],
  "malaga": ["cadiz", "sevilla", "cordoba", "granada"],
  "cadiz": ["malaga", "sevilla"],
  "sevilla": ["huelva", "cadiz", "malaga", "cordoba", "badajoz"],
  "huelva": ["sevilla", "badajoz"],
  "badajoz": ["caceres", "toledo", "ciudad real", "cordoba", "sevilla", "huelva"],
  "caceres": ["salamanca", "avila", "toledo", "badajoz"],
  "toledo": ["madrid", "avila", "caceres", "ciudad real", "albacete", "cuenca"],
  "avila": ["madrid", "segovia", "valladolid", "salamanca", "toledo"],
  "segovia": ["madrid", "guadalajara", "soria", "burgos", "valladolid", "avila"],
  "soria": ["burgos", "segovia", "guadalajara", "zaragoza", "la rioja"],
  "la rioja": ["alava", "navarra", "soria", "burgos"],
  "alava": ["burgos", "la rioja", "navarra", "bizkaia", "gipuzkoa"],
  "bizkaia": ["cantabria", "burgos", "alava", "gipuzkoa"],
  "gipuzkoa": ["alava", "navarra", "bizkaia"],
  "navarra": ["alava", "gipuzkoa", "la rioja", "zaragoza", "huesca"],
  "coruna": ["lugo", "pontevedra"],
  "lugo": ["coruna", "pontevedra", "ourense", "leon", "asturias"],
  "pontevedra": ["coruna", "lugo", "ourense"],
  "ourense": ["lugo", "pontevedra", "zamora", "leon"],
  "castellon": ["tarragona", "teruel", "valencia"],
  "palencia": ["leon", "cantabria", "burgos", "valladolid"],
};

/** Normaliza una provincia: minúsculas, sin tildes y sin espacios extra. */
function normalizarProvincia(p: string): string {
  return p
    .toLocaleLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

/**
 * Busca el siguiente técnico disponible para una provincia,
 * Devuelve { tecnicoId, provinciaUsada } o null si no hay ninguno.
  */
 async function buscarTecnicoDisponible(
   provincia: string,
   leadId: string,
   excluir: string[] = [],
 ): Promise<{ tecnicoId: string; provinciaUsada: string } | null> {
   // Exclusión permanente: el dueño (arturo) nunca recibe encargos asignados automáticamente
   const EXCLUIR_PERMANENTE = ["4b805c7b-0bbf-490d-8000-21c620cbf30f"];
   const excluirTotal = [...new Set([...excluir, ...EXCLUIR_PERMANENTE])];

   // Técnicos activos y verificados. El filtro por provincia se hace en JS con
   // comparación normalizada (sin acentos/case) para ser inmune a variaciones de
   // formato ("Córdoba" vs "Cordoba"). Antes se usaba ILIKE, que no ignora tildes.
   const { data: tecnicos } = await supabase
     .from("tecnicos")
     .select("id, nombre, email, modelo_pago, saldo_creditos, premium_hasta, verificado, activo, provincia")
     .eq("activo", true)
     .eq("verificado", true);

   if (!tecnicos || tecnicos.length === 0) return null;

   const provNorm = normalizarProvincia(provincia);

   let provReal: string | null = null;
   const candidatos = tecnicos.filter((t) => {
     if (excluirTotal.includes(t.id)) return false;
     // la columna provincia puede contener varias provincias separadas por coma
     const provinciasTecnico = String(t.provincia ?? "").split(",").map((x) => x.trim());
     const idx = provinciasTecnico.findIndex((x) => normalizarProvincia(x) === provNorm);
     if (idx === -1) return false;
     if (provReal === null) provReal = provinciasTecnico[idx];
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

   return ordenados.length > 0
     ? { tecnicoId: ordenados[0].id, provinciaUsada: provReal || provincia }
     : null;
 }

 /**
  * Busca técnico primero en la provincia exacta del lead y, si no hay,
  * prueba con las provincias liminales definidas en PROVINCIAS_LIMITROFES.
  * Devuelve { tecnicoId, provinciaUsada, limitrofe } o null.
  */
 async function buscarTecnicoConFallback(
   provincia: string,
   leadId: string,
   excluir: string[] = [],
 ): Promise<{ tecnicoId: string; provinciaUsada: string; limitrofe: boolean } | null> {
   if (provincia) {
     const directo = await buscarTecnicoDisponible(provincia, leadId, excluir);
     if (directo) return { tecnicoId: directo.tecnicoId, provinciaUsada: directo.provinciaUsada, limitrofe: false };
   }

   const limitrofes = PROVINCIAS_LIMITROFES[normalizarProvincia(provincia)] ?? [];
   for (const lim of limitrofes) {
     const res = await buscarTecnicoDisponible(lim, leadId, excluir);
     if (res) return { tecnicoId: res.tecnicoId, provinciaUsada: res.provinciaUsada, limitrofe: true };
   }

   return null;
 }

/**
 * Notifica al técnico asignado.
 * - Primeros 3 leads: email con datos completos del lead + instrucciones de onboarding.
 * - Del 4º en adelante: email breve con enlace a la página desindexada (panel-tecnico.html?token=).
 * Incrementa el contador leads_recibidos del técnico.
  * @param limitrofeAsignacion indica que fue una asignación desde provincia limítrofe (zona próxima).
 */
async function notificarAsignacion(leadId: string, tecnicoId: string, limitrofeAsignacion = false) {
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
  // Aviso que se muestra cuando es asignación por zona próxima (limítrofe)
  const avisoZona = limitrofeAsignacion
    ? `<p style="color:#b45309;background:#fef3c7;border-radius:8px;padding:10px 14px;font-size:13px;margin:12px 0;"><strong>Zona próxima:</strong> no había técnico disponible en ${lead.provincia || lead.codigo_postal}, por lo que este encargo se te asigna por estar en una provincia limítrofe. Confirma con el cliente si puedes desplazarte.</p>`
    : "";

  let html: string;
  let subject: string;

  // ⚠️ ANTI-ELUSIÓN: NUNCA se envían teléfono/email del cliente en claro al técnico.
  // El contacto se hace SOLO a través del chat de la plataforma (chat.html?encargo=ID),
  // de modo que CertificadoYa mantiene la intermediación y la comisión del 18%.
  const chatUrl = `${WEB}/chat.html?encargo=${leadId}`;
  subject = `📋 Nuevo encargo en ${lead.provincia || lead.codigo_postal}${limitrofeAsignacion ? " (zona próxima)" : ""} — CertificadoYa`;
  html = `
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
      <h2 style="color: #16a34a;">📋 Nuevo encargo asignado</h2>
      <p>Hola <strong>${tecnico.nombre}</strong>, tienes un nuevo encargo en <strong>${lead.provincia || lead.codigo_postal}</strong>${lead.m2 ? `, ${lead.m2} m²${lead.tipo_inmueble ? " (" + lead.tipo_inmueble + ")" : ""}` : ""}.</p>
      ${avisoZona}
      <div style="background:#f2f8f4; border-radius:12px; padding:18px 20px; margin:18px 0; font-size:14px; line-height:1.7; color:#1a2b23;">
        <strong style="color:#0f6b3d;">Cómo funciona CertificadoYa:</strong><br>
        1. <strong>Contactas al cliente desde el chat de la plataforma</strong> (botón abajo). El cliente ya pagó a CertificadoYa.<br>
        2. <strong>Acordáis la visita y emites el CEE</strong> como técnico colegiado.<br>
        3. <strong>Subes el certificado</strong> y nosotros gestionamos el registro oficial.<br>
        4. <strong>Cobras tú (82%)</strong> al completar — la comisión del 18% se resta automáticamente.<br><br>
        <span style="color:#b45309;">El contacto directo (teléfono/email fuera de la plataforma) no está disponible hasta que el servicio se cierra en CertificadoYa, para garantizar la protección de ambas partes y tu pago.</span>
      </div>
      <p style="margin-top: 20px;"><a href="${chatUrl}" style="background:#16a34a;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;">💬 Contactar al cliente (chat de CertificadoYa)</a></p>
      <p style="color:#888;font-size:12px;">Este es el encargo nº ${recibidos}. El cliente ya pagó y el importe está retenido hasta la entrega del CEE.</p>
    </div>`;

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
      .select("id, nombre_cliente, provincia, estado, tecnico_asignado, notas")
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

    const resultado = await buscarTecnicoConFallback(lead.provincia || "", leadId, excluir);

    if (!resultado) {
      // No hay técnico disponible en la provincia ni en las limítrofes → dejar pendiente para reintento
      await supabase.from("leads").update({ estado: "pendiente" }).eq("id", leadId);
      return new Response(JSON.stringify({ success: false, message: "Sin técnico disponible en la zona", reintentar: true }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    const { tecnicoId, provinciaUsada, limitrofe } = resultado;

    // Asignar. Si es asignación liminal, lo marcamos en `notas` para trazabilidad.
    const camposUpdate: Record<string, unknown> = {
      estado: "pendiente_tecnico",
      tecnico_asignado: tecnicoId,
      fecha_asignacion: new Date().toISOString(),
    };
    if (limitrofe) {
      const marca = `[Asignación limítrofe ${new Date().toISOString().slice(0, 10)}] Sin técnico en ${lead.provincia}; asignado a técnico de ${provinciaUsada}.`;
      camposUpdate.notas = lead.notas ? `${lead.notas}\n${marca}` : marca;
    }
    const { error: updErr } = await supabase
      .from("leads")
      .update(camposUpdate)
      .eq("id", leadId);

    if (updErr) {
      return new Response(JSON.stringify({ error: updErr.message }), { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }

    // Notificar
    await notificarAsignacion(leadId, tecnicoId, limitrofe);

    return new Response(JSON.stringify({ success: true, tecnico_id: tecnicoId, message: limitrofe ? "Asignado automáticamente a técnico de provincia limítrofe" : "Asignado automáticamente", provincia: provinciaUsada, limitrofe }), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
  } catch (err) {
    return new Response(JSON.stringify({ success: false, error: err.message }), { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }
});
