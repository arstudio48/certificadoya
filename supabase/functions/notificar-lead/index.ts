// Follow this setup guide if this is your first Supabase Edge Function:
// https://supabase.com/docs/guides/functions/quickstart

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";

interface Lead {
  nombre_cliente: string;
  telefono_cliente: string;
  email_cliente: string | null;
  codigo_postal: string;
  zona: string;
  m2: number;
  tipo_inmueble: string;
  presupuesto_min: number;
  presupuesto_max: number;
}

interface WebhookPayload {
  type: "INSERT";
  table: string;
  record: Lead;
  schema: "public";
}

async function enviarEmail(lead: Lead): Promise<boolean> {
  const presupuestoTexto = `${lead.presupuesto_min}€ – ${lead.presupuesto_max}€`;
  const emailCliente = lead.email_cliente ? `Email cliente: ${lead.email_cliente}` : "No proporcionó email";

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "CertificadoYa <leads@certificadoya.es>",
        to: "artbriher@gmail.com",
        subject: `🔔 Nuevo lead - ${lead.zona} - ${lead.nombre_cliente}`,
        html: `
          <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #16a34a;">🟢 Nuevo cliente interesado</h2>
            <table style="width: 100%; border-collapse: collapse;">
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Nombre</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.nombre_cliente}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="tel:${lead.telefono_cliente}">${lead.telefono_cliente}</a></td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${emailCliente}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Zona</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.zona} (CP: ${lead.codigo_postal})</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.m2} m² - ${lead.tipo_inmueble}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Presupuesto</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${presupuestoTexto}</td></tr>
            </table>
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
              Responde al cliente lo antes posible para cerrar el trato.
            </p>
          </div>
        `,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Resend error:", res.status, errorText);
      return false;
    }
    console.log("Email enviado correctamente");
    return true;
  } catch (err) {
    console.error("Error enviando email:", err);
    return false;
  }
}

serve(async (req) => {
  // Solo aceptamos POST de Supabase
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const payload: WebhookPayload = await req.json();
    const lead = payload.record;

    console.log("Nuevo lead recibido:", lead.nombre_cliente, "-", lead.zona);

    // Enviar email
    const emailOk = await enviarEmail(lead);

    return new Response(
      JSON.stringify({ success: true, email: emailOk }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("Error:", err);
    return new Response(
      JSON.stringify({ success: false, error: err.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
