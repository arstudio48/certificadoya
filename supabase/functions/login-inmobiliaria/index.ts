import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import nodemailer from 'npm:nodemailer'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

// ── Gmail SMTP (para códigos OTP) ──
const GMAIL_USER = Deno.env.get('GMAIL_USER') || ''
const GMAIL_PASS = Deno.env.get('GMAIL_APP_PASSWORD') || ''

function getMailer() {
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: { user: GMAIL_USER, pass: GMAIL_PASS },
  })
}

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// ── Helper: enviar email por SMTP (Gmail) ──
async function sendEmailSmtp(to: string, subject: string, content: string, html?: string): Promise<{ok: boolean, error?: string}> {
  if (!GMAIL_USER || !GMAIL_PASS) {
    return { ok: false, error: 'SMTP not configured' }
  }
  try {
    const mailer = getMailer()
    await mailer.sendMail({
      from: `CertificadoYa <${GMAIL_USER}>`,
      to,
      subject,
      text: content,
      html,
    })
    return { ok: true }
  } catch (e) {
    return { ok: false, error: String(e).slice(0, 300) }
  }
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

    // Buscar la inmobiliaria por email
    const { data: inmobiliaria, error: findError } = await supabase
      .from('inmobiliarias')
      .select('id, nombre, email')
      .eq('email', email)
      .maybeSingle()

    if (findError || !inmobiliaria) {
      return new Response(JSON.stringify({ error: 'Email no encontrado. ¿Estás registrado como inmobiliaria?' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Generar código OTP de 6 dígitos
    const codigo = String(Math.floor(100000 + Math.random() * 900000))

    // Guardar código en BD
    await supabase
      .from('inmobiliarias')
      .update({
        token: codigo,
        updated_at: new Date().toISOString()
      })
      .eq('id', inmobiliaria.id)

    // ── Enviar código por email (Gmail SMTP) ──
    let emailOk = false
    let emailError = ''
    try {
      const htmlBody = `
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
          <div style="text-align: center; background: #16a34a; color: white; padding: 2rem; border-radius: 12px 12px 0 0;">
            <h2 style="margin: 0; font-size: 1.5rem;">🏢 Acceso inmobiliarias</h2>
          </div>
          <div style="background: white; padding: 2rem; border: 1px solid #e8ece6; border-radius: 0 0 12px 12px;">
            <p style="margin: 0 0 1rem; color: #2d3a1f; font-size: 1rem;">Hola <strong>${inmobiliaria.nombre}</strong>,</p>
            <p style="margin: 0 0 1.5rem; color: #6b7b5e; font-size: .9rem;">Tu código de acceso al panel de inmobiliarias es:</p>
            <div style="background: #f0fdf4; padding: 1.5rem; text-align: center; border-radius: 12px; margin-bottom: 1.5rem;">
              <span style="font-size: 2.2rem; font-weight: 800; color: #16a34a; letter-spacing: 8px;">${codigo}</span>
            </div>
            <p style="color: #9aab8a; font-size: .8rem;">Este código expira en 10 minutos. No lo compartas con nadie.</p>
            <p style="color: #9aab8a; font-size: .8rem; margin-top: 1rem;">🌐 <a href="https://www.certificadoya.es/inmobiliarias/panel.html" style="color: #16a34a;">Acceder al panel</a></p>
          </div>
        </div>
      `
      const result = await sendEmailSmtp(
        email,
        `🔐 Tu código de acceso — CertificadoYa Inmobiliarias`,
        `Tu código de acceso es: ${codigo}\n\nExpira en 10 minutos. No lo compartas con nadie.\n\nAccede: https://www.certificadoya.es/inmobiliarias/panel.html`,
        htmlBody
      )
      emailOk = result.ok
      if (!emailOk) emailError = result.error || 'Unknown SMTP error'
    } catch (_e) {
      emailError = String(_e).slice(0, 200)
    }

    return new Response(JSON.stringify({
      success: true,
      message: emailOk
        ? 'Código enviado a tu email. Revisa tu bandeja de entrada.'
        : 'Código enviado. Si no recibes el email, revisa tu carpeta de spam.',
      inmobiliariaId: inmobiliaria.id,
      enviadoA: {
        email: emailOk
      },
      debug: emailError ? { emailError } : undefined
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
