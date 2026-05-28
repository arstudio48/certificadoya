import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders })
  }

  try {
    const { email } = await req.json()

    if (!email) {
      return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Verificar que el técnico existe
    const { data: tecnico, error: findError } = await supabase
      .from('tecnicos')
      .select('id, nombre, email')
      .eq('email', email)
      .eq('activo', true)
      .maybeSingle()

    if (findError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Email no encontrado. ¿Estás registrado como técnico?' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Generar código OTP de 6 dígitos
    const codigo = String(Math.floor(100000 + Math.random() * 900000))
    const expira = new Date(Date.now() + 10 * 60 * 1000).toISOString()

    // Guardar código en BD
    await supabase
      .from('tecnicos')
      .update({
        token: codigo,
        updated_at: new Date().toISOString()
      })
      .eq('id', tecnico.id)

    // Enviar código por email
    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: 'CertificadoYa <info@certificadoya.es>',
          to: email,
          subject: `🔐 Tu código de acceso — CertificadoYa`,
          html: `
            <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
              <div style="text-align: center; background: #547c24; color: white; padding: 2rem; border-radius: 12px 12px 0 0;">
                <h2 style="margin: 0; font-size: 1.5rem;">🔐 Acceso técnicos</h2>
              </div>
              <div style="background: white; padding: 2rem; border: 1px solid #e8ece6; border-radius: 0 0 12px 12px;">
                <p style="margin: 0 0 1rem; color: #2d3a1f; font-size: 1rem;">Hola <strong>${tecnico.nombre}</strong>,</p>
                <p style="margin: 0 0 1.5rem; color: #6b7b5e; font-size: .9rem;">Tu código de acceso al panel de técnicos es:</p>
                <div style="background: #f3f9eb; padding: 1.5rem; text-align: center; border-radius: 12px; margin-bottom: 1.5rem;">
                  <span style="font-size: 2.2rem; font-weight: 800; color: #547c24; letter-spacing: 8px;">${codigo}</span>
                </div>
                <p style="color: #9aab8a; font-size: .8rem;">Este código expira en 10 minutos. No lo compartas con nadie.</p>
              </div>
            </div>
          `
        })
      })
    } catch (_) { /* error de email no crítico — el código se guardó en BD */ }

    return new Response(JSON.stringify({
      success: true,
      message: 'Código enviado a tu email. Revisa tu bandeja de entrada.',
      tecnicoId: tecnico.id
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
