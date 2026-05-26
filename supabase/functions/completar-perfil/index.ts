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
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }

  try {
    const { token, email, titulacion, colegiado, colegio, provincias, iban, plan } = await req.json()

    if (!token || !email || !titulacion || !colegiado || !colegio || !provincias) {
      return new Response(JSON.stringify({ error: 'Faltan campos obligatorios' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Buscar al técnico por email (registrado pero no completado aún)
    const { data: tecnico, error: searchError } = await supabase
      .from('tecnicos')
      .select('id, nombre')
      .eq('email', email)
      .eq('activo', true)
      .eq('verificado', false)
      .single()

    if (searchError || !tecnico) {
      return new Response(JSON.stringify({ error: 'Token o email inválido' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Actualizar perfil completo
    const provinciaStr = Array.isArray(provincias) ? provincias.join(',') : provincias
    const { error: updateError } = await supabase
      .from('tecnicos')
      .update({
        titulacion,
        numero_colegiado: colegiado,
        provincia: provinciaStr,
        iban: iban || null,
        plan: plan || 'por-lead',
        verificado: false
      })
      .eq('id', tecnico.id)

    if (updateError) throw updateError

    // ── Enviar emails ──

    // Email al técnico
    const provinciasTexto = Array.isArray(provincias) ? provincias.join(', ') : provincias
    try {
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: email,
          subject: "✅ Tu registro en CertificadoYa está pendiente de verificación",
          html: `
            <div style="font-family: 'Montserrat', sans-serif; max-width: 560px; margin: 0 auto; padding: 20px;">
              <div style="text-align: center; margin-bottom: 24px;">
                <div style="display: inline-block; background: #edf4e5; border-radius: 50%; width: 64px; height: 64px; line-height: 64px; font-size: 28px;">✅</div>
              </div>
              <h1 style="color: #2d3a1f; font-size: 1.3rem; text-align: center; margin-bottom: 8px;">¡Registro completado!</h1>
              <p style="color: #6b7b5e; text-align: center; font-size: 0.9rem; margin-bottom: 24px;">
                Hola <strong>${tecnico.nombre}</strong>, hemos recibido tu solicitud correctamente.
              </p>
              <div style="background: #f7f9f6; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                <p style="margin: 0 0 8px; color: #3d4f2e; font-size: 0.85rem;"><strong>Resumen de tu perfil:</strong></p>
                <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📋 Titulación: ${titulacion}</p>
                <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">🆔 Nº Colegiado: ${colegiado} (${colegio})</p>
                <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📍 Provincias: ${provinciasTexto}</p>
              </div>
              <p style="color: #6b7b5e; font-size: 0.88rem; line-height: 1.6;">
                <strong>¿Qué pasa ahora?</strong><br>
                1. Nuestro equipo revisará tu documentación.<br>
                2. En un plazo de 24-48h verificaremos tu colegiación.<br>
                3. Recibirás un email de confirmación cuando tu cuenta esté activa.<br><br>
                Mientras tanto, puedes echar un ojo a nuestros <a href="https://www.certificadoya.es/blog/?cat=tecnicos" style="color: #547c24;">recursos para técnicos</a>.
              </p>
              <hr style="border: none; border-top: 1px solid #e8ece6; margin: 24px 0;">
              <p style="color: #9aab8a; font-size: 0.78rem; text-align: center;">
                CertificadoYa · certificadoya.es · Si tienes dudas, responde a este email.
              </p>
            </div>
          `
        })
      });
    } catch (_) { /* email al técnico no crítico */ }

    // Email a CertificadoYa (aviso interno)
    try {
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: "artbriher@gmail.com",
          subject: `🆕 Nuevo técnico registrado — ${tecnico.nombre}`,
          html: `
            <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
              <h2 style="color: #547c24;">🆕 Nuevo técnico registrado</h2>
              <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Nombre</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${tecnico.nombre}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${email}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Titulación</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${titulacion}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Colegiado</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${colegiado} (${colegio})</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Provincias</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${provinciasTexto}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Plan</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${plan || 'por-lead'}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">IBAN</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${iban || 'No proporcionado'}</td></tr>
              </table>
              <hr style="border: none; border-top: 1px solid #e8ece6; margin: 20px 0;">
              <p style="color: #9aab8a; font-size: 0.78rem;">
                Revisa y verifica este técnico desde el panel de administración.
              </p>
            </div>
          `
        })
      });
    } catch (_) { /* email interno no crítico */ }

    return new Response(JSON.stringify({
      success: true,
      message: 'Perfil completado correctamente. Tu solicitud está pendiente de verificación.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
