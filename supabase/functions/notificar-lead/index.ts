import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE_ROLE_KEY = Deno.env.get("SERVICE_ROLE_KEY") ?? "";
const CERTI_EMAIL = Deno.env.get("CERTIFICADOYA_EMAIL") ?? "artbriher@gmail.com";

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

interface LeadData {
  id: number;
  nombre_cliente: string;
  email_cliente: string | null;
  telefono_cliente: string;
  codigo_postal: string;
  provincia: string | null;
  m2: number | null;
  tipo_inmueble: string | null;
  presupuesto_min: number | null;
  presupuesto_max: number | null;
}

// ─── NOTIFICACIÓN AL ADMIN ───────────────────────────────────────────
async function enviarNotificacionAdmin(lead: LeadData): Promise<boolean> {
  const emailCliente = lead.email_cliente
    ? `Email cliente: ${lead.email_cliente}`
    : "No proporcionó email";

  const zona = lead.provincia || `CP ${lead.codigo_postal}`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "CertificadoYa <leads@certificadoya.es>",
        to: CERTI_EMAIL,
        subject: `🔔 Nuevo lead - ${zona} - ${lead.nombre_cliente}`,
        html: `
          <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #16a34a;">🟢 Nuevo cliente interesado</h2>
            <table style="width: 100%; border-collapse: collapse;">
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Nombre</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.nombre_cliente}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="tel:${lead.telefono_cliente}">${lead.telefono_cliente}</a></td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${emailCliente}</td></tr>
              <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Zona</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${zona}</td></tr>
              ${lead.m2 ? `<tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.m2} m²${lead.tipo_inmueble ? ' - ' + lead.tipo_inmueble : ''}</td></tr>` : ''}
              ${lead.presupuesto_min ? `<tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Presupuesto</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${lead.presupuesto_min}€${lead.presupuesto_max ? ' – ' + lead.presupuesto_max + '€' : ''}</td></tr>` : ''}
            </table>
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
              Responde al cliente lo antes posible.
            </p>
          </div>
        `,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Resend error (admin):", res.status, errorText);
      return false;
    }
    console.log("Notificación admin enviada");
    return true;
  } catch (err) {
    console.error("Error enviando notificación admin:", err);
    return false;
  }
}

// ─── CONFIRMACIÓN AL CLIENTE ─────────────────────────────────────────
async function enviarConfirmacionCliente(lead: LeadData): Promise<boolean> {
  if (!lead.email_cliente) {
    console.log("Cliente sin email, se omite confirmación");
    return false;
  }

  const zona = lead.provincia || `CP ${lead.codigo_postal}`;

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "CertificadoYa <leads@certificadoya.es>",
        to: lead.email_cliente,
        subject: "Recibimos tu solicitud - CertificadoYa",
        html: `
          <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="text-align: center; padding: 20px 0;">
              <h1 style="color: #d4af37; margin: 0; font-size: 28px;">CertificadoYa</h1>
              <p style="color: #666; font-size: 14px;">Certificados energéticos profesionales</p>
            </div>
            <div style="background: #f9fafb; border-radius: 12px; padding: 24px;">
              <h2 style="color: #1b1b1f; margin-top: 0;">✅ Hemos recibido tu solicitud</h2>
              <p style="color: #333; line-height: 1.6;">
                Hola <strong>${lead.nombre_cliente}</strong>,<br><br>
                Gracias por confiar en CertificadoYa. Hemos recibido tu solicitud de presupuesto y
                uno de nuestros técnicos en <strong>${zona}</strong> te contactará
                al <strong>${lead.telefono_cliente}</strong> en menos de 24 horas.
              </p>
              ${lead.m2 ? `<div style="background: white; border-radius: 8px; padding: 16px; margin: 16px 0; border: 1px solid #e5e7eb;">
                <h3 style="color: #1b1b1f; margin: 0 0 12px 0; font-size: 16px;">Resumen</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                  ${lead.m2 ? `<tr><td style="padding: 6px 0; color: #666;">Superficie</td><td style="padding: 6px 0; text-align: right;">${lead.m2} m²</td></tr>` : ''}
                  ${lead.tipo_inmueble ? `<tr><td style="padding: 6px 0; color: #666;">Tipo</td><td style="padding: 6px 0; text-align: right;">${lead.tipo_inmueble}</td></tr>` : ''}
                </table>
              </div>` : ''}
              <p style="color: #666; font-size: 13px; line-height: 1.5;">
                Si tienes alguna duda, responde a este email.
              </p>
            </div>
            <div style="text-align: center; padding: 20px 0; color: #999; font-size: 12px;">
              <p>CertificadoYa — certificadoya.es</p>
            </div>
          </div>
        `,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Resend error (cliente):", res.status, errorText);
      return false;
    }
    console.log("Confirmación enviada al cliente");
    return true;
  } catch (err) {
    console.error("Error enviando confirmación al cliente:", err);
    return false;
  }
}

// ─── MAIN ────────────────────────────────────────────────────────────
serve(async (req) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const lead: LeadData = await req.json();
    console.log("Lead recibido:", lead.nombre_cliente, "-", lead.telefono_cliente);

    // 1. Notificar al admin
    const adminOk = await enviarNotificacionAdmin(lead);

    // 2. Enviar confirmación al cliente (si tiene email)
    const clienteOk = await enviarConfirmacionCliente(lead);

    // 3. Marcar como notificado en la BD
    if (adminOk || clienteOk) {
      await supabase
        .from("leads")
        .update({
          email_notificado_confirmacion: clienteOk,
          email_notificado_asignacion: adminOk,
        })
        .eq("id", lead.id);
    }

    return new Response(
      JSON.stringify({ success: true, admin: adminOk, cliente: clienteOk }),
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
