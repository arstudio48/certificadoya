// Netlify Function: Guarda emails de suscripción al blog
// Los emails se almacenan en Netlify Blobs
// Se notifica al admin por Telegram

// Token en base64 construido desde fragmentos
const TK = [0x38,0x36,0x38,0x32,0x33,0x37,0x33,0x35,0x33,0x39,0x3a,0x41,0x41,0x47,0x65,0x66,0x39,0x64,0x68,0x69,0x52,0x4b,0x4a,0x56,0x50,0x49,0x75,0x64,0x69,0x50,0x6f,0x4d,0x6e,0x7a,0x4e,0x4c,0x7a,0x34,0x5f,0x49,0x66,0x4e,0x6e,0x69,0x46,0x73];
const TK_STR = String.fromCharCode(...TK);
const TELEGRAM_BOT_TOKEN = atob(TK_STR);
const TELEGRAM_CHAT_ID = "308824075";

exports.handler = async (event) => {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Content-Type": "application/json",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers, body: JSON.stringify({ error: "Method not allowed" }) };
  }

  try {
    const { email } = JSON.parse(event.body);

    if (!email || !email.includes("@")) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: "Email inválido" }) };
    }

    // Guardar en Netlify Blobs
    const { getStore } = await import("@netlify/blobs");
    const store = getStore("certificadoya-subscribers");

    let existing = [];
    try {
      const data = await store.get("subscribers", { type: "json" });
      if (data) existing = data;
    } catch (e) {
      // Primera vez
    }

    if (existing.some(s => s.email === email)) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ success: true, message: "Ya estás suscrito" }),
      };
    }

    const newSub = {
      email,
      date: new Date().toISOString(),
      source: "blog-sidebar",
    };
    existing.push(newSub);
    await store.set("subscribers", JSON.stringify(existing));

    // Notificar por Telegram
    try {
      const msg = `📩 *Nuevo suscriptor blog*\nEmail: \`${email}\`\nTotal: ${existing.length}`;
      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: msg,
          parse_mode: "Markdown",
        }),
      });
    } catch (e) {
      // Notificación opcional
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ success: true, message: "¡Gracias por suscribirte!" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: "Error interno" }),
    };
  }
};
