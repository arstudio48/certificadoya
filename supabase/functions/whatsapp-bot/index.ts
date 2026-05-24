// WhatsApp Bot — CertificadoYa
// Meta Cloud API Webhook
// Desplegar con: supabase functions deploy whatsapp-bot --no-verify-jwt

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

// ── Config ──
const VERIFY_TOKEN = Deno.env.get("WHATSAPP_VERIFY_TOKEN") || "certificadoya2026";
const WHATSAPP_TOKEN = Deno.env.get("WHATSAPP_TOKEN") || "";
const WHATSAPP_PHONE_ID = Deno.env.get("WHATSAPP_PHONE_ID") || "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") || "";
const NOTIFY_EMAIL = "artbriher@gmail.com";

// ── Tipos ──
interface WhatsAppMessage {
  object: string;
  entry: Array<{
    id: string;
    changes: Array<{
      value: {
        messaging_product: string;
        metadata: { display_phone_number: string; phone_number_id: string };
        contacts?: Array<{ profile: { name: string }; wa_id: string }>;
        messages?: Array<{
          from: string;
          id: string;
          timestamp: string;
          type: "text" | "interactive" | "button";
          text?: { body: string };
          interactive?: { type: string; button_reply?: { id: string; title: string }; list_reply?: { id: string; title: string } };
        }>;
      };
    }>;
  }>;
}

// ── Respuestas ──
const MENU_PRINCIPAL = `🏠 *CertificadoYa — Bot*

Elige una opción:

1️⃣ *Presupuesto rápido*
Calcula tu certificado al instante

2️⃣ *¿Cómo funciona?*
Pasos para conseguir tu CEE

3️⃣ *Zonas disponibles*
Dónde operamos

4️⃣ *Hablar con un humano*
Te contactamos en minutos

5️⃣ *Horario y contacto*

Responde con el número (1-5)`;

const MENU_OPTIONS: Record<string, string> = {
  "1": `💰 *Presupuesto rápido*

Calcula tu presupuesto directamente en nuestra web:

👉 https://www.certificadoya.es/#presupuesto-card

O dime tu *código postal* y *metros cuadrados* y te lo calculo ahora mismo.`,
  "2": `📋 *¿Cómo funciona?*

1. *Calcula* — Introduce tus datos en la web
2. *Te contactamos* — Un técnico te llama
3. *Visita técnica* — Mediciones en 20 min
4. *Certificado listo* — Lo recibes en 24h registrado

👉 https://www.certificadoya.es/`,
  "3": `📍 *Zonas disponibles*

Operamos en toda España:
Madrid, Barcelona, Valencia, Sevilla, Alicante, Málaga, Murcia, Asturias, Bilbao, Zaragoza, Valladolid, Granada, Cádiz, Baleares, Canarias... y más de 40 provincias.

👉 Ver todas: https://www.certificadoya.es/`,
  "4": `📞 *Hablar con un humano*

Déjame tu *nombre y teléfono* y te llamamos en menos de 15 minutos.

O escríbenos directamente a:
✉️ hola@certificadoya.es`,
  "5": `⏰ *Horario y contacto*

👨‍💻 *Atención online:* 24h / 7 días
📞 *Teléfono:* +34 6****3002
✉️ *Email:* hola@certificadoya.es
🌐 *Web:* https://www.certificadoya.es/

🟢 Respuesta automática inmediata. Para atención personal, elige opción 4.`,
};

// ── Helper: enviar WhatsApp ──
async function sendWhatsApp(to: string, text: string): Promise<boolean> {
  try {
    const res = await fetch(
      `https://graph.facebook.com/v21.0/${WHATSAPP_PHONE_ID}/messages`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${WHATSAPP_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messaging_product: "whatsapp",
          to,
          type: "text",
          text: { body: text },
        }),
      }
    );
    return res.ok;
  } catch {
    return false;
  }
}

// ── Helper: notificar por email ──
async function notifyEmail(userName: string, phone: string, message: string) {
  if (!RESEND_API_KEY) return;
  try {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "WhatsApp Bot <leads@certificadoya.es>",
        to: NOTIFY_EMAIL,
        subject: `💬 Nuevo WhatsApp - ${userName} - ${phone}`,
        html: `
          <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
            <h2 style="color:#16a34a;">🟢 Nuevo mensaje de WhatsApp</h2>
            <table style="width:100%;border-collapse:collapse">
              <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Nombre</td><td style="padding:8px;border-bottom:1px solid #eee">${userName}</td></tr>
              <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Teléfono</td><td style="padding:8px;border-bottom:1px solid #eee"><a href="tel:${phone}">${phone}</a></td></tr>
              <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Mensaje</td><td style="padding:8px;border-bottom:1px solid #eee">${message}</td></tr>
            </table>
            <p style="margin-top:1rem;color:#6b7280;font-size:.85rem">
              <a href="https://wa.me/34${phone}">Abrir chat en WhatsApp</a>
            </p>
          </div>
        `,
      }),
    });
  } catch {
    // Silencio
  }
}

// ── Lógica del bot ──
function processMessage(text: string): string {
  const t = text.trim().toLowerCase();

  // Saludo → menú
  if (/^(hola|buenas|hey|hello|hi|buenos días|buenas tardes|🙋|👋)/i.test(t)) {
    return MENU_PRINCIPAL;
  }

  // Opciones del menú (1-5)
  if (/^[12345]$/.test(t.trim())) {
    return MENU_OPTIONS[t.trim()] || MENU_PRINCIPAL;
  }

  // Palabras clave
  if (/precio|cuanto|cuesta|tarifa|presupuesto|coste|costo/i.test(t)) {
    return MENU_OPTIONS["1"] + `\n\n_Para volver al menú, escribe "menú"_`;
  }
  if (/como funciona|pasos|proceso|cómo funciona/i.test(t)) {
    return MENU_OPTIONS["2"] + `\n\n_Para volver al menú, escribe "menú"_`;
  }
  if (/zona|provincia|madrid|barcelona|donde|disponible/i.test(t)) {
    return MENU_OPTIONS["3"] + `\n\n_Para volver al menú, escribe "menú"_`;
  }
  if (/humano|persona|hablar|atencion|ayuda|contacto/i.test(t)) {
    return MENU_OPTIONS["4"] + `\n\n_Para volver al menú, escribe "menú"_`;
  }
  if (/horario|telefono|email|correo/i.test(t)) {
    return MENU_OPTIONS["5"] + `\n\n_Para volver al menú, escribe "menú"_`;
  }
  if (/menu|menú|opcion|opción|volver|atrás/i.test(t)) {
    return MENU_PRINCIPAL;
  }

  // Si parece un código postal (5 dígitos) → presupuesto
  if (/^\d{5}$/.test(t.trim())) {
    return `📍 C.P. ${t.trim()}\n\nPara calcular tu presupuesto exacto, entra en nuestra web:\n👉 https://www.certificadoya.es/#presupuesto-card\n\nO dime también los *metros cuadrados* de la vivienda.`;
  }

  // Si no entiende → menú
  return `No he entendido tu mensaje. ¿Puedes elegir una opción?\n\n${MENU_PRINCIPAL}`;
}

// ── Handler principal ──
serve(async (req) => {
  const url = new URL(req.url);

  // ── Webhook Verification (GET) ──
  if (req.method === "GET") {
    const mode = url.searchParams.get("hub.mode");
    const token = url.searchParams.get("hub.verify_token");
    const challenge = url.searchParams.get("hub.challenge");

    if (mode === "subscribe" && token === VERIFY_TOKEN) {
      return new Response(challenge, { status: 200 });
    }
    return new Response("Verification failed", { status: 403 });
  }

  // ── Incoming Message (POST) ──
  if (req.method === "POST") {
    try {
      const body: WhatsAppMessage = await req.json();

      for (const entry of body.entry || []) {
        for (const change of entry.changes || []) {
          const value = change.value;

          // Skip non-message events
          if (!value.messages || value.messages.length === 0) continue;

          for (const msg of value.messages) {
            const from = msg.from; // Número de teléfono
            const userName = value.contacts?.[0]?.profile?.name || "Usuario";
            let text = "";

            if (msg.type === "text" && msg.text?.body) {
              text = msg.text.body;
            } else if (msg.type === "interactive") {
              if (msg.interactive?.button_reply) {
                text = msg.interactive.button_reply.title;
              } else if (msg.interactive?.list_reply) {
                text = msg.interactive.list_reply.title;
              }
            }

            if (!text) continue;

            // Procesar mensaje
            const reply = processMessage(text);

            // Enviar respuesta
            await sendWhatsApp(from, reply);

            // Si pide humano, notificar por email
            if (text.trim() === "4" || /humano|persona|hablar/i.test(text)) {
              await notifyEmail(userName, from, text);
            }
          }
        }
      }

      return new Response("OK", { status: 200 });
    } catch (err) {
      console.error("Error processing webhook:", err);
      return new Response("OK", { status: 200 }); // Siempre 200 a Meta
    }
  }

  return new Response("Method not allowed", { status: 405 });
});
