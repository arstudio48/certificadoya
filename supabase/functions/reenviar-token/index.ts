// Edge Function: reenviar-token
// Reenvía el código (token) de acceso al técnico por email si lo perdió.
// Deploy: supabase functions deploy reenviar-token --no-verify-jwt
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

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  try {
    const { email } = await req.json()
    if (!email) return new Response(JSON.stringify({ error: 'email requerido' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

    const { data: tecnico, error } = await supabase
      .from('tecnicos')
      .select('id, nombre, email, token, activo')
      .eq('email', email)
      .eq('activo', true)
      .single()

    if (error || !tecnico) {
      return new Response(JSON.stringify({ error: 'No encontramos un técnico activo con ese email' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    const panelUrl = `https://www.certificadoya.es/panel-tecnico.html?token=${tecnico.token}`
    const html = `
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px;">
      <h2 style="color:#16a34a;">Tu código de acceso — CertificadoYa</h2>
      <p>Hola ${tecnico.nombre?.split(' ')[0] || 'técnico'}, aquí tienes tu código para acceder al panel:</p>
      <p style="font-size:20px;background:#f0faf2;padding:12px 16px;border-radius:8px;color:#0f6b3d;word-break:break-all;"><code>${tecnico.token}</code></p>
      <p>En móvil, usa este enlace y el código se rellenará solo:</p>
      <p><a href="${panelUrl}" style="background:#16a34a;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;">Abrir mi panel</a></p>
      <p style="color:#888;font-size:12px;">En PC/tablet copia el código en el campo "Tu código de técnico".</p>
    </div>`

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: EMAIL_REMITENTE, to: tecnico.email, subject: 'Tu código de acceso a CertificadoYa', html })
    })
    if (!res.ok) return new Response(JSON.stringify({ error: 'Error enviando email' }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

    return new Response(JSON.stringify({ success: true, email: tecnico.email }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
