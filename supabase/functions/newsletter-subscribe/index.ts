import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') ?? ''
const SUPABASE_URL = 'https://wypgqpgjlookbhuaiyxa.supabase.co'

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Método no permitido' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }

  try {
    const body = await req.json()
    const { email, userType, timestamp, source } = body

    // Validar email
    const emailClean = (email || '').trim().toLowerCase()
    if (!emailClean || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailClean)) {
      return new Response(JSON.stringify({ error: 'Email inválido' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Validar userType
    if (!userType || !['technician', 'owner'].includes(userType)) {
      return new Response(JSON.stringify({ error: 'Tipo de usuario inválido' }), {
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

    // Verificar si ya existe
    const checkRes = await fetch(
      `${SUPABASE_URL}/rest/v1/newsletter_subscribers?email=eq.${encodeURIComponent(emailClean)}&select=id,active`,
      {
        headers: {
          'apikey': token,
          'Authorization': `Bearer ${token}`
        }
      }
    )
    const existing = await checkRes.json()

    if (existing && existing.length > 0) {
      const sub = existing[0]
      if (sub.active) {
        return new Response(JSON.stringify({
          success: true,
          message: 'Ya estás suscrito',
          alreadySubscribed: true
        }), {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }
      // Reactivar si estaba inactivo
      await fetch(`${SUPABASE_URL}/rest/v1/newsletter_subscribers?id=eq.${sub.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'apikey': token,
          'Authorization': `Bearer ${token}`,
          'Prefer': 'return=representation'
        },
        body: JSON.stringify({
          active: true,
          user_type: userType,
          source: source || 'website'
        })
      })

      // Enviar confirmación de reactivación
      if (RESEND_API_KEY) {
        await enviarConfirmacion(emailClean, userType)
      }

      return new Response(JSON.stringify({ success: true, message: 'Suscripción reactivada' }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Insertar nuevo suscriptor
    const insertRes = await fetch(`${SUPABASE_URL}/rest/v1/newsletter_subscribers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': token,
        'Authorization': `Bearer ${token}`,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({
        email: emailClean,
        user_type: userType,
        source: source || 'website',
        confirmed: true
      })
    })

    if (!insertRes.ok) {
      const errText = await insertRes.text()
      console.error('Error insertando suscriptor:', errText)
      return new Response(JSON.stringify({ error: 'Error al guardar la suscripción' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Enviar confirmación
    if (RESEND_API_KEY) {
      await enviarConfirmacion(emailClean, userType)
    }

    return new Response(JSON.stringify({ success: true, message: 'Suscripción creada' }), {
      status: 201,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (err) {
    console.error('Error en newsletter-subscribe:', err)
    return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})

async function enviarConfirmacion(email: string, userType: string) {
  const tipoTexto = userType === 'technician' ? '👷 contenidos para técnicos' : '🏠 contenidos para propietarios'

  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: "CertificadoYa <info@certificadoya.es>",
      to: email,
      subject: `📬 ¡Gracias por suscribirte a CertificadoYa!`,
      html: `
        <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
          <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
              <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
              <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Certificado de Eficiencia Energética</div>
            </div>
            <div style="padding:35px 40px 10px">
              <div style="font-size:48px;text-align:center;margin-bottom:10px">📬</div>
              <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px;text-align:center">¡Gracias por suscribirte!</h1>
              <p style="font-size:15px;color:#6b7b5e;line-height:1.5;text-align:center">A partir de ahora recibirás cada semana <strong>${tipoTexto}</strong> directamente en tu bandeja de entrada.</p>
            </div>
            <div style="padding:10px 40px 25px;text-align:center">
              <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Mientras esperas al próximo envío, visita nuestro blog:</p>
              <a href="https://www.certificadoya.es/blog/" style="display:inline-block;background:#fff;color:#547c24;text-decoration:none;padding:10px 24px;border-radius:8px;font-weight:600;font-size:14px;border:2px solid #547c24">Visitar blog →</a>
            </div>
            <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
              <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética en toda España</p>
              <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
              <p style="margin-top:10px;font-size:11px;color:#b8c8a9">Si no deseas recibir más correos, puedes <a href="https://www.certificadoya.es/desuscribirse.html?email=${email}" style="color:#547c24;text-decoration:underline">darte de baja aquí</a>.</p>
              <p style="margin-top:4px;font-size:11px;color:#b8c8a9">Si no te has suscrito tú, ignora este email.</p>
            </div>
          </div>
        </div>
      `,
    }),
  }).catch(e => console.error("Error enviando confirmación newsletter:", e));
}
