// Edge Function: bienvenida-tecnico
// Envía email de bienvenida institucional a un técnico con info del funcionamiento
// y enlace al panel para seleccionar leads. NO incluye datos de clientes.
// Deploy: supabase functions deploy bienvenida-tecnico --no-verify-jwt
// Secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''
const EMAIL_REMITENTE = 'CertificadoYa <info@certificadoya.es>'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

function htmlBienvenida(nombre: string, token: string): string {
  const panelUrl = `https://www.certificadoya.es/panel-tecnico.html?token=${token}`
  const primerNombre = (nombre || 'Técnico').split(' ')[0]
  return `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0A0A0B;color:#e8e8ea;margin:0;padding:40px 20px;">
  <div style="max-width:560px;margin:0 auto;background:#111114;border:1px solid #1e1e22;border-radius:12px;padding:32px;">
    <h1 style="color:#00ffbb;font-size:24px;margin:0 0 8px;letter-spacing:-.02em;">¡Bienvenido a CertificadoYa, ${primerNombre}!</h1>
    <p style="color:#8a8a92;font-size:14px;margin:0 0 20px;">La red de técnicos de certificación energética de España.</p>

    <p style="color:#e8e8ea;font-size:15px;line-height:1.6;">Ya formas parte de la red de <strong>CertificadoYa.es</strong>. Te explicamos cómo funciona y cómo empezar a recibir encargos:</p>

    <div style="background:#0e1a14;border:1px solid #1e3a2a;border-radius:10px;padding:18px 20px;margin:20px 0;">
      <h3 style="color:#00ffbb;font-size:16px;margin:0 0 10px;">Cómo funciona (y cómo cobras)</h3>
      <ol style="color:#cfcfd6;font-size:14px;line-height:1.7;margin:0;padding-left:20px;">
        <li>El <strong>cliente paga a CertificadoYa</strong> por adelantado. Tu comisión (82%) queda retenida.</li>
        <li>Te asignamos el encargo y ves los <strong>datos del inmueble</strong> (zona, m², tipo) en tu panel.</li>
        <li>Contactas al cliente por el <strong>chat de la plataforma</strong> (nunca se facilita su teléfono para evitar que cerréis por fuera y pierdas tu pago).</li>
        <li>Acordáis la visita y <strong>emites el CEE</strong> como técnico colegiado.</li>
        <li>Subes el nº de registro o PDF y <strong>cobras tú (82%)</strong> al verificar la entrega. El 18% es nuestra comisión.</li>
      </ol>
    </div>

    <div style="background:#16110e;border:1px solid #3a2a1e;border-radius:10px;padding:18px 20px;margin:20px 0;">
      <h3 style="color:#ffb454;font-size:16px;margin:0 0 10px;">⚠️ Para recibir leads necesitas saldo o suscripción</h3>
      <p style="color:#cfcfd6;font-size:14px;line-height:1.6;margin:0;">Tu alta está activa, pero para que te asignemos encargos debes tener <strong>saldo de créditos o suscripción premium</strong> cargados. Sin saldo, los leads entran en cola pero no se te asignan hasta que lo tengas. Puedes gestionarlo desde tu panel.</p>
    </div>

    <div style="text-align:center;margin:28px 0;">
      <a href="${panelUrl}" style="background:#00ffbb;color:#000;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;display:inline-block;">Acceder a mi panel de técnicos</a>
    </div>

    <p style="color:#8a8a92;font-size:13px;line-height:1.6;">Desde el panel puedes ver tus encargos, seleccionar leads disponibles y gestionar tu saldo. Si tienes dudas, responde a este correo.</p>

    <hr style="border:0;border-top:1px solid #1e1e22;margin:24px 0;">
    <p style="color:#8a8a92;font-size:11px;line-height:1.5;">CertificadoYa.es · Tratamos tus datos con base en el consentimiento (Art. 6.1.a RGPD). Puedes ejercer tus derechos en <a href="mailto:privacidad@certificadoya.es" style="color:#00ffbb;">privacidad@certificadoya.es</a>.</p>
  </div>
</body></html>`
}

async function enviarBienvenida(tecnico: any) {
  const respuesta = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: EMAIL_REMITENTE,
      to: tecnico.email,
      subject: 'Bienvenido a CertificadoYa — tu panel de técnicos está listo',
      html: htmlBienvenida(tecnico.nombre, tecnico.token),
    }),
  })
  if (!respuesta.ok) {
    const error = await respuesta.text()
    throw new Error(`Resend fallo para ${tecnico.email}: ${error}`)
  }
  return await respuesta.json()
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  try {
    const body = await req.json()
    const { email, token, todos } = body

    // Modo "todos": enviar a todos los técnicos activos
    if (todos === true) {
      const { data: tecnicos, error } = await supabase
        .from('tecnicos')
        .select('id, nombre, email, token, activo')
        .eq('activo', true)
      if (error) throw error
      const resultados = []
      for (const t of tecnicos || []) {
        try {
          await enviarBienvenida(t)
          resultados.push({ email: t.email, ok: true })
        } catch (e) {
          resultados.push({ email: t.email, ok: false, error: e.message })
        }
      }
      return new Response(JSON.stringify({ success: true, enviados: resultados.length, detalle: resultados }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Modo individual
    if (!email && !token) {
      return new Response(JSON.stringify({ error: 'email o token requerido' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    const query = supabase.from('tecnicos').select('id, nombre, email, token, activo')
    if (token) query.eq('token', token); else query.eq('email', email)
    const { data: tecnico, error } = await query.single()
    if (error || !tecnico) {
      return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), {
        status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    await enviarBienvenida(tecnico)
    return new Response(JSON.stringify({ success: true, email: tecnico.email }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
