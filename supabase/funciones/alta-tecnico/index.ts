// supabase/functions/alta-tecnico/index.ts
// Edge Function — recibe alta de técnico, guarda en BD, envía doble opt-in vía Resend.
// Desplegar: supabase functions deploy alta-tecnico --no-verify-jwt

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const CABECERAS_CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
};

const ORIGEN_PERMITIDO = "https://certificadoya.es";
const EMAIL_REMITENTE = "CertificadoYa <alta@certificadoya.es>";
const EMAIL_ADMIN = "arturobriher@gmail.com";

interface DatosAlta {
  nombre: string;
  email: string;
  telefono: string;
  provincia: string;
  titulacion: string;
  modulos: string;
  mensaje?: string;
  origen?: string;
  fecha?: string;
}

function generarToken(): string {
  return crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "");
}

function validarEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function enviarEmailConfirmacion(datos: DatosAlta, token: string, apiKeyResend: string) {
  const urlConfirmacion = `https://certificadoya.es/confirmar-alta/?token=${token}`;

  const cuerpoHtml = `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0A0A0B;color:#e8e8ea;margin:0;padding:40px 20px;">
  <div style="max-width:560px;margin:0 auto;background:#111114;border:1px solid #1e1e22;border-radius:12px;padding:32px;">
    <h1 style="color:#00ffbb;font-size:24px;margin:0 0 20px;letter-spacing:-.02em;">Confirma tu alta</h1>
    <p style="color:#e8e8ea;font-size:15px;line-height:1.6;">Hola ${datos.nombre.split(" ")[0]},</p>
    <p style="color:#8a8a92;font-size:15px;line-height:1.6;">
      Hemos recibido tu solicitud para unirte a la red de t\u00e9cnicos de <strong style="color:#e8e8ea;">CertificadoYa.es</strong>.
      Para completar el alta y verificar que este correo es tuyo, pulsa el bot\u00f3n:
    </p>
    <div style="text-align:center;margin:32px 0;">
      <a href="${urlConfirmacion}" style="background:#00ffbb;color:#000;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;display:inline-block;">Confirmar mi alta</a>
    </div>
    <p style="color:#8a8a92;font-size:13px;line-height:1.6;">
      Si no has solicitado este alta, ignora este correo. El enlace caduca en 7 d\u00edas.
    </p>
    <hr style="border:0;border-top:1px solid #1e1e22;margin:24px 0;">
    <p style="color:#8a8a92;font-size:12px;line-height:1.5;">
      <strong>Datos recibidos:</strong><br>
      Provincia: ${datos.provincia}<br>
      Titulaci\u00f3n: ${datos.titulacion}<br>
      M\u00f3dulos RD 659/2025: ${datos.modulos}
    </p>
    <p style="color:#8a8a92;font-size:11px;margin-top:24px;">
      CertificadoYa.es \u00b7 Tratamos tus datos con base en el consentimiento (Art. 6.1.a RGPD). Puedes ejercer tus derechos en <a href="mailto:privacidad@certificadoya.es" style="color:#00ffbb;">privacidad@certificadoya.es</a>.
    </p>
  </div>
</body></html>`;

  const respuesta = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKeyResend}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: EMAIL_REMITENTE,
      to: datos.email,
      subject: "Confirma tu alta como t\u00e9cnico \u2014 CertificadoYa",
      html: cuerpoHtml,
    }),
  });

  if (!respuesta.ok) {
    const error = await respuesta.text();
    throw new Error(`Resend fallo: ${error}`);
  }

  return await respuesta.json();
}

async function enviarNotificacionAdmin(datos: DatosAlta, apiKeyResend: string) {
  const html = `
<h2>Nueva solicitud de t\u00e9cnico</h2>
<p><strong>Nombre:</strong> ${datos.nombre}</p>
<p><strong>Email:</strong> ${datos.email}</p>
<p><strong>Tel\u00e9fono:</strong> ${datos.telefono}</p>
<p><strong>Provincia:</strong> ${datos.provincia}</p>
<p><strong>Titulaci\u00f3n:</strong> ${datos.titulacion}</p>
<p><strong>M\u00f3dulos RD 659/2025:</strong> ${datos.modulos}</p>
<p><strong>Comentarios:</strong> ${datos.mensaje || "\u2014"}</p>
<hr>
<p style="font-size:12px;color:#666">Origen: ${datos.origen || "\u2014"}</p>`;

  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKeyResend}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: EMAIL_REMITENTE,
      to: EMAIL_ADMIN,
      subject: `[CY] Nuevo t\u00e9cnico: ${datos.nombre} \u2014 ${datos.provincia}`,
      html,
    }),
  });
}

serve(async (peticion) => {
  if (peticion.method === "OPTIONS") {
    return new Response("ok", { headers: CABECERAS_CORS });
  }

  if (peticion.method !== "POST") {
    return new Response(JSON.stringify({ error: "M\u00e9todo no permitido" }), {
      status: 405,
      headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
    });
  }

  try {
    const datos: DatosAlta = await peticion.json();

    if (!datos.nombre || !datos.email || !datos.telefono || !datos.provincia || !datos.titulacion) {
      return new Response(JSON.stringify({ error: "Faltan campos obligatorios" }), {
        status: 400,
        headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
      });
    }

    if (!validarEmail(datos.email)) {
      return new Response(JSON.stringify({ error: "Email no v\u00e1lido" }), {
        status: 400,
        headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
      });
    }

    const clienteSupabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const apiKeyResend = Deno.env.get("RESEND_API_KEY");
    if (!apiKeyResend) throw new Error("RESEND_API_KEY no configurada");

    const { data: existente } = await clienteSupabase
      .from("tecnicos_captacion")
      .select("id, confirmado")
      .eq("email", datos.email)
      .maybeSingle();

    if (existente?.confirmado) {
      return new Response(JSON.stringify({ error: "Ya est\u00e1s dado de alta con este correo." }), {
        status: 409,
        headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
      });
    }

    const token = generarToken();

    const { error: errorInsert } = await clienteSupabase
      .from("tecnicos_captacion")
      .upsert({
        nombre: datos.nombre,
        email: datos.email,
        telefono: datos.telefono,
        provincia: datos.provincia,
        titulacion: datos.titulacion,
        modulos_rd659: datos.modulos,
        mensaje: datos.mensaje || null,
        origen: datos.origen || null,
        token_confirmacion: token,
        confirmado: false,
        creado_en: new Date().toISOString(),
      }, { onConflict: "email" });

    if (errorInsert) throw errorInsert;

    await enviarEmailConfirmacion(datos, token, apiKeyResend);
    await enviarNotificacionAdmin(datos, apiKeyResend);

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("Error:", error);
    return new Response(JSON.stringify({ error: "Error interno del servidor" }), {
      status: 500,
      headers: { ...CABECERAS_CORS, "Content-Type": "application/json" },
    });
  }
});
