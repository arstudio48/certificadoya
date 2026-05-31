import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') ?? ''

const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const body = await req.json()
    const { action, name, email, phone, cp, m2, tipo, zona, precioMin, precioMax, leadId } = body

    if (action === 'solicitar') {
      // Notificar a técnicos sobre lead existente
      // Esta ruta se llama desde el frontend después de guardar el lead
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ==== CREAR LEAD ====
    const nombre = (name || '').trim()
    const telefono = (phone || '').trim()
    const cpVal = (cp || '').trim()
    if (!nombre || !telefono || !cpVal) {
      return new Response(JSON.stringify({
        error: 'Faltan campos requeridos: nombre, teléfono y CP son obligatorios'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const token = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    if (!token) {
      return new Response(JSON.stringify({ error: 'Error de configuración del servidor' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const emailVal = (email || '').trim() || null
    const zonaVal = (zona || '').trim() || null
    const m2Val = m2 != null ? Math.round(Number(m2)) : null
    const precioMinVal = precioMin != null ? Math.round(Number(precioMin)) : null
    const precioMaxVal = precioMax != null ? Math.round(Number(precioMax)) : null

    // INSERT directo en la tabla leads
    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': token,
        'Authorization': `Bearer ${token}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({
        nombre_cliente: nombre,
        telefono_cliente: telefono,
        email_cliente: emailVal,
        codigo_postal: cpVal,
        provincia: zonaVal,
        m2: m2Val,
        tipo_inmueble: tipo || 'piso',
        presupuesto_min: precioMinVal,
        presupuesto_max: precioMaxVal,
        fuente: 'web',
        estado: 'nuevo'
      })
    })

    const data = await res.json()

    if (!res.ok) {
      return new Response(JSON.stringify({
        error: data.message || JSON.stringify(data)
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // --- Enviar confirmación al cliente (si tiene email) ---
    if (emailVal && RESEND_API_KEY) {
      const presupuestoTexto = precioMinVal && precioMaxVal
        ? `${precioMinVal}€ – ${precioMaxVal}€`
        : 'a consultar'

      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: emailVal,
          subject: `✅ Solicitud recibida - CertificadoYa`,
          html: `
            <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
              <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                  <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                  <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Certificado de Eficiencia Energética</div>
                </div>
                <div style="padding:35px 40px 10px">
                  <div style="font-size:48px;text-align:center;margin-bottom:10px">✅</div>
                  <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px;text-align:center">¡Solicitud recibida!</h1>
                  <p style="font-size:15px;color:#6b7b5e;line-height:1.5;text-align:center">Hemos recibido tu solicitud de certificado energético. <strong>Un técnico de tu zona te llamará pronto.</strong></p>
                </div>
                <div style="padding:10px 40px 20px">
                  <div style="background:#f3f9eb;border-radius:8px;padding:16px 20px">
                    <p style="font-size:13px;color:#5a7a3a;margin:0 0 10px;font-weight:600">📋 Resumen de tu solicitud</p>
                    <table style="width:100%;border-collapse:collapse;font-size:13px">
                      <tr><td style="padding:4px 0;color:#6b7b5e">Nombre</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">${nombre}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Teléfono</td><td style="padding:4px 0;color:#1a1a1a">${telefono}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Zona</td><td style="padding:4px 0;color:#1a1a1a">${zonaVal || '—'} (CP: ${cpVal})</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Inmueble</td><td style="padding:4px 0;color:#1a1a1a">${m2Val || '—'} m² · ${tipo || 'Piso'}</td></tr>
                      <tr><td style="padding:4px 0;color:#6b7b5e">Presupuesto</td><td style="padding:4px 0;color:#1a1a1a;font-weight:600">${presupuestoTexto}</td></tr>
                    </table>
                  </div>
                </div>
                <div style="padding:0 40px 25px;text-align:center">
                  <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Mientras tanto, puedes consultar guías útiles en nuestro blog:</p>
                  <a href="https://www.certificadoya.es/blog/" style="display:inline-block;background:#fff;color:#547c24;text-decoration:none;padding:10px 24px;border-radius:8px;font-weight:600;font-size:14px;border:2px solid #547c24">Visitar blog →</a>
                </div>
                <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                  <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética en toda España</p>
                  <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                </div>
              </div>
            </div>
          `,
        }),
      }).catch(e => console.error("Error enviando confirmación al cliente:", e));
    }

    return new Response(JSON.stringify({
      success: true,
      leadId: data.id || data[0]?.id,
      mensaje: 'Solicitud recibida. Te contactaremos pronto.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
