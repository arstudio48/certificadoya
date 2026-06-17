import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') ?? ''

serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  }

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: corsHeaders })
  }

  try {
    const { nombre, email, telefono, titulacion, provincias } = await req.json()

    if (!nombre || !email || !telefono) {
      return new Response(JSON.stringify({ error: 'Faltan campos obligatorios' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)
    
    // Check if email already exists
    const { data: existing } = await supabase
      .from('tecnicos')
      .select('id')
      .eq('email', email)
      .maybeSingle()

    if (existing) {
      // Enviar email recordando que ya está registrado
      if (RESEND_API_KEY) {
        await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${RESEND_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: "CertificadoYa <info@certificadoya.es>",
            to: email,
            subject: `🔐 Ya estás registrado en CertificadoYa, ${nombre}`,
            html: `
              <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
                <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                  <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                    <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                    <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Red de técnicos certificadores</div>
                  </div>
                  <div style="padding:35px 40px 10px 40px">
                    <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px 0">Ya tienes cuenta en CertificadoYa</h1>
                    <p style="font-size:15px;color:#6b7b5e;line-height:1.5;margin:0">Hemos recibido tu intento de registro, pero ya estás dado de alta en nuestra plataforma.</p>
                  </div>
                  <div style="padding:20px 40px 35px;text-align:center">
                    <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Para acceder a los trabajos disponibles, solo tienes que introducir tu email en la página de acceso y te enviaremos un código.</p>
                    <a href="https://www.certificadoya.es/pool-encargos.html" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:14px 32px;border-radius:8px;font-weight:600;font-size:15px">Acceder a trabajos →</a>
                  </div>
                  <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                    <p style="margin:0 0 4px">CertificadoYa.es — Trabajos para técnicos certificadores</p>
                    <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                  </div>
                </div>
              </div>
            `,
          }),
        }).catch(e => console.error("Error enviando email de ya registrado:", e));
      }
      return new Response(JSON.stringify({ error: 'Este email ya está registrado. Te hemos enviado un email con instrucciones para acceder.' }), { status: 409, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Insert technician
    const { data, error } = await supabase
      .from('tecnicos')
      .insert({
        email,
        nombre,
        telefono,
        titulacion: titulacion || null,
        provincias: provincias || null,
        verificado: false,
        activo: true
      })
      .select('id')
      .single()

    if (error) throw error

    // Generate token
    const token = crypto.randomUUID().replace(/-/g, '').slice(0, 24)

    // --- Enviar email de bienvenida al técnico ---
    if (RESEND_API_KEY) {
      const titulacionNombre: Record<string, string> = {
        'Arquitecto': 'Arquitecto',
        'Aparejador / Arquitecto técnico': 'Aparejador / Arquitecto Técnico',
        'Ingeniero de Edificación': 'Ingeniero de Edificación',
        'Ingeniero Industrial': 'Ingeniero Industrial',
        'Ingeniero Técnico': 'Ingeniero Técnico',
        'FP Edificación y Obra Civil': 'FP Edificación y Obra Civil',
        'Otra titulación habilitante': titulacion
      }

      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: email,
          subject: `👷 ¡Bienvenido a CertificadoYa, ${nombre}!`,
          html: `
            <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
              <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                  <div style="font-size:28px;font-weight:700;color:#fff">CertificadoYa</div>
                  <div style="font-size:13px;color:#b8d4a0;margin-top:4px">Red de técnicos certificadores</div>
                </div>
                <div style="padding:35px 40px 10px 40px">
                  <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 6px 0">¡Bienvenido a CertificadoYa, ${nombre}!</h1>
                  <p style="font-size:15px;color:#6b7b5e;line-height:1.5;margin:0">Gracias por unirte a nuestra red de técnicos certificadores. Ya estamos revisando tu solicitud.</p>
                </div>
                <div style="padding:10px 40px">
                  <table style="width:100%;border-collapse:collapse">
                    <tr><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#6b7b5e;font-size:14px;width:120px">Nombre</td><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#1a1a1a;font-size:14px;font-weight:600">${nombre}</td></tr>
                    <tr><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#6b7b5e;font-size:14px">Titulación</td><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#1a1a1a;font-size:14px;font-weight:600">${titulacionNombre[titulacion] || titulacion}</td></tr>
                    <tr><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#6b7b5e;font-size:14px">Email</td><td style="padding:8px 0;border-bottom:1px solid #eef4e8;color:#1a1a1a;font-size:14px">${email}</td></tr>
                    <tr><td style="padding:8px 0;color:#6b7b5e;font-size:14px">Teléfono</td><td style="padding:8px 0;color:#1a1a1a;font-size:14px">${telefono}</td></tr>
                  </table>
                </div>
                <div style="padding:20px 40px 35px;text-align:center">
                  <p style="font-size:14px;color:#6b7b5e;line-height:1.5">Para empezar a recibir trabajos, completa tu perfil profesional:</p>
                  <a href="https://www.certificadoya.es/panel-tecnicos/completar-perfil.html?token=${token}&email=${encodeURIComponent(email)}" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;font-size:15px">Completar perfil →</a>
                </div>
                <div style="background:#f3f9eb;padding:20px 40px">
                  <p style="font-size:13px;color:#5a7a3a;margin:0 0 8px"><strong>📋 Próximos pasos:</strong></p>
                  <ol style="font-size:13px;color:#5a7a3a;margin:0;padding-left:18px;line-height:1.8">
                    <li>Completa tu perfil profesional</li>
                    <li>Selecciona las provincias donde trabajas</li>
                    <li>Empieza a recibir solicitudes de clientes</li>
                    <li>Tú eliges qué trabajos aceptar</li>
                  </ol>
                </div>
                <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                  <p style="margin:0 0 4px">CertificadoYa.es — Certificación energética rápida y fácil</p>
                  <p style="margin:0"><a href="https://www.certificadoya.es/" style="color:#547c24">certificadoya.es</a> · <a href="mailto:info@certificadoya.es" style="color:#547c24">info@certificadoya.es</a></p>
                </div>
              </div>
            </div>
          `,
        }),
      }).catch(e => console.error("Error enviando bienvenida:", e));

      // --- Notificar al admin ---
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "CertificadoYa <info@certificadoya.es>",
          to: "artbriher@gmail.com",
          subject: `👷 Nuevo técnico registrado - ${nombre}`,
          html: `
            <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
              <h2 style="color:#547c24">🟢 Nuevo técnico registrado</h2>
              <table style="width:100%;border-collapse:collapse">
                <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Nombre</td><td style="padding:8px;border-bottom:1px solid #eee">${nombre}</td></tr>
                <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Titulación</td><td style="padding:8px;border-bottom:1px solid #eee">${titulacion}</td></tr>
                <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Email</td><td style="padding:8px;border-bottom:1px solid #eee">${email}</td></tr>
                <tr><td style="padding:8px;border-bottom:1px solid #eee;font-weight:600">Teléfono</td><td style="padding:8px;border-bottom:1px solid #eee"><a href="tel:${telefono}">${telefono}</a></td></tr>
              </table>
              <p style="margin-top:20px;color:#666;font-size:14px">Revisa su perfil y verifícalo en el panel de administración.</p>
            </div>
          `,
        }),
      }).catch(e => console.error("Error notificando admin:", e));
    }

    return new Response(JSON.stringify({
      success: true,
      id: data.id,
      token: token,
      message: 'Registro completado. Completa tu perfil profesional.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
