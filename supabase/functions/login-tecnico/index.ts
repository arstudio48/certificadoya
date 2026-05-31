import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import nodemailer from 'npm:nodemailer'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''
const WHATSAPP_TOKEN = Deno.env.get('WHATSAPP_TOKEN') || ''
const WHATSAPP_PHONE_ID = Deno.env.get('WHATSAPP_PHONE_ID') || ''

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

// ── Helper: enviar WhatsApp ──
async function sendWhatsApp(to: string, text: string): Promise<boolean> {
  if (!WHATSAPP_TOKEN || !WHATSAPP_PHONE_ID) return false
  try {
    const res = await fetch(
      `https://graph.facebook.com/v21.0/${WHATSAPP_PHONE_ID}/messages`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${WHATSAPP_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messaging_product: 'whatsapp',
          to,
          type: 'text',
          text: { body: text },
        }),
      }
    )
    return res.ok
  } catch {
    return false
  }
}

// ── Formatear teléfono a internacional ──
function formatPhone(phone: string): string {
  // Si ya tiene +, lo dejamos igual
  if (phone.startsWith('+')) return phone.replace(/[^0-9+]/g, '')
  // Si empieza por 00, convertir a +
  if (phone.startsWith('00')) return '+' + phone.slice(2)
  // Número español (6/7/9 dígitos) → +34
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 9 && /^[679]/.test(digits)) return '34' + digits
  // Si ya tiene código de país sin +
  if (digits.length > 9) return digits
  return '34' + digits // asumimos España por defecto
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

    // Verificar que el técnico existe (traemos también teléfono)
    const { data: tecnico, error: findError } = await supabase
      .from('tecnicos')
      .select('id, nombre, email, telefono')
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

    // ── 1. Enviar código por email (Gmail SMTP) ──
    let emailOk = false
    let emailError = ''
    try {
      const htmlBody = `
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
      const result = await sendEmailSmtp(
        email,
        `🔐 Tu código de acceso — CertificadoYa`,
        `Tu código de acceso es: ${codigo}\n\nExpira en 10 minutos. No lo compartas con nadie.`,
        htmlBody
      )
      emailOk = result.ok
      if (!emailOk) emailError = result.error || 'Unknown SMTP error'
    } catch (_e) {
      emailError = String(_e).slice(0, 200)
    }

    // ── 2. Enviar código por WhatsApp si tiene teléfono ──
    let wppOk = false
    if (tecnico.telefono) {
      const telefonoInt = formatPhone(tecnico.telefono)
      const mensajeWpp = `🔐 *CertificadoYa — Código de acceso*\n\nHola ${tecnico.nombre},\n\nTu código para acceder al panel de técnicos es:\n\n*${codigo}*\n\nEste código expira en 10 minutos. No lo compartas con nadie.\n\n🌐 certificadoya.es/pool-encargos.html`
      wppOk = await sendWhatsApp(telefonoInt, mensajeWpp)
    }

    return new Response(JSON.stringify({
      success: true,
      message: emailOk
        ? 'Código enviado a tu email y WhatsApp (si tienes teléfono registrado). Revisa ambos.'
        : 'Código enviado. Si no recibes el email, revisa tu WhatsApp.',
      tecnicoId: tecnico.id,
      enviadoA: {
        email: emailOk,
        whatsapp: wppOk
      },
      debug: emailError ? { emailError } : undefined
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
