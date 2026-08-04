// Edge Function: bienvenida-cliente
// Email de bienvenida al CLIENTE explicando el proceso de CertificadoYa.
// Se envía tras el pago (el cliente ya pagó, luego puede recibir datos del flujo).
// Deploy: supabase functions deploy bienvenida-cliente --no-verify-jwt
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

function htmlBienvenida(nombre: string, zona: string): string {
  const primerNombre = (nombre || 'Cliente').split(' ')[0]
  return `
<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0A0A0B;color:#e8e8ea;margin:0;padding:40px 20px;">
  <div style="max-width:560px;margin:0 auto;background:#111114;border:1px solid #1e1e22;border-radius:12px;padding:32px;">
    <h1 style="color:#00ffbb;font-size:24px;margin:0 0 8px;letter-spacing:-.02em;">¡Hola ${primerNombre}! Tu certificado está en camino</h1>
    <p style="color:#8a8a92;font-size:14px;margin:0 0 20px;">Gracias por confiar en CertificadoYa.es</p>

    <p style="color:#e8e8ea;font-size:15px;line-height:1.6;">Has contratado tu certificado de eficiencia energética con <strong>CertificadoYa</strong>. Te contamos cómo trabajamos para que tengas total tranquilidad:</p>

    <div style="background:#0e1a14;border:1px solid #1e3a2a;border-radius:10px;padding:18px 20px;margin:20px 0;">
      <h3 style="color:#00ffbb;font-size:16px;margin:0 0 10px;">El proceso, paso a paso</h3>
      <ol style="color:#cfcfd6;font-size:14px;line-height:1.7;margin:0;padding-left:20px;">
        <li><strong>Pagaste por adelantado</strong> — tu importe está retenido de forma segura en CertificadoYa hasta que el trabajo está hecho.</li>
        <li>Te asignamos un <strong>técnico colegiado</strong> de tu zona (arquitecto o ingeniero de edificación).</li>
        <li>El técnico te contacta por el <strong>chat de la plataforma</strong> para acordar la visita. Así garantizamos que seas tú quien recibe el servicio contratado.</li>
        <li>El técnico realiza la visita y emite el <strong>Certificado Energético (CEE)</strong> oficial.</li>
        <li>Nosotros gestionamos el <strong>registro en el registro oficial</strong> de tu comunidad autónoma.</li>
        <li>Recibes tu certificado y, si todo fue bien, <strong>liberamos el pago al técnico</strong>. Si algo falla, tu dinero está protegido.</li>
      </ol>
    </div>

    <div style="background:#16110e;border:1px solid #3a2a1e;border-radius:10px;padding:18px 20px;margin:20px 0;">
      <h3 style="color:#ffb454;font-size:16px;margin:0 0 10px;">🛡️ Tu garantía</h3>
      <p style="color:#cfcfd6;font-size:14px;line-height:1.6;margin:0;">Al pagar a través de CertificadoYa (no directamente al técnico), tu pago queda <strong>protegido</strong>. Solo se libera al técnico cuando el CEE está emitido y registrado. Si el servicio no se completa, recuperas tu importe.</p>
    </div>

    <div style="text-align:center;margin:28px 0;">
      <a href="https://www.certificadoya.es/chat.html" style="background:#00ffbb;color:#000;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;display:inline-block;">Abrir mi chat con el técnico</a>
    </div>

    <p style="color:#8a8a92;font-size:13px;line-height:1.6;">En breve te confirmaremos el técnico asignado. Cualquier duda, responde a este correo.</p>

    <hr style="border:0;border-top:1px solid #1e1e22;margin:24px 0;">
    <p style="color:#8a8a92;font-size:11px;line-height:1.5;">CertificadoYa.es · Tratamos tus datos con base en la ejecución del contrato (Art. 6.1.b RGPD). Puedes ejercer tus derechos en <a href="mailto:privacidad@certificadoya.es" style="color:#00ffbb;">privacidad@certificadoya.es</a>.</p>
  </div>
</body></html>`
}

async function enviar(email: string, nombre: string, zona: string) {
  const respuesta = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: EMAIL_REMITENTE,
      to: email,
      subject: 'Tu certificado energético con CertificadoYa — así trabajamos',
      html: htmlBienvenida(nombre, zona),
    }),
  })
  if (!respuesta.ok) {
    const error = await respuesta.text()
    throw new Error(`Resend fallo para ${email}: ${error}`)
  }
  return await respuesta.json()
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  try {
    const body = await req.json()
    const { email, lead_id, todos } = body

    // Modo "todos": clientes con pago confirmado (leads en estado nuevo/asignado) de las últimas 24h
    if (todos === true) {
      const hace24h = new Date(Date.now() - 24 * 3600 * 1000).toISOString()
      const { data: leads, error } = await supabase
        .from('leads')
        .select('id, nombre_cliente, email_cliente, provincia, codigo_postal, estado')
        .eq('estado', 'nuevo')
        .gte('created_at', hace24h)
      if (error) throw error
      const resultados = []
      for (const l of leads || []) {
        if (!l.email_cliente) { resultados.push({ lead: l.id, ok: false, error: 'sin email' }); continue }
        try {
          await enviar(l.email_cliente, l.nombre_cliente || 'Cliente', l.provincia || (l.codigo_postal || ''))
          resultados.push({ lead: l.id, ok: true })
        } catch (e) {
          resultados.push({ lead: l.id, ok: false, error: e.message })
        }
      }
      return new Response(JSON.stringify({ success: true, enviados: resultados.length, detalle: resultados }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Individual por email o lead_id
    if (lead_id) {
      const { data: l, error } = await supabase.from('leads').select('*').eq('id', lead_id).single()
      if (error || !l || !l.email_cliente) return new Response(JSON.stringify({ error: 'lead sin email' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      await enviar(l.email_cliente, l.nombre_cliente || 'Cliente', l.provincia || (l.codigo_postal || ''))
      return new Response(JSON.stringify({ success: true, email: l.email_cliente }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }
    if (email) {
      await enviar(email, body.nombre || 'Cliente', body.zona || '')
      return new Response(JSON.stringify({ success: true, email }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }
    return new Response(JSON.stringify({ error: 'email, lead_id o todos requerido' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
