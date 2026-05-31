import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import nodemailer from 'npm:nodemailer'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const GMAIL_USER = Deno.env.get('GMAIL_USER') || ''
const GMAIL_PASS = Deno.env.get('GMAIL_APP_PASSWORD') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function getMailer() {
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: { user: GMAIL_USER, pass: GMAIL_PASS },
  })
}

async function sendOtp(email: string, codigo: string): Promise<boolean> {
  if (!GMAIL_USER || !GMAIL_PASS) return false
  try {
    const mailer = getMailer()
    await mailer.sendMail({
      from: `CertificadoYa <${GMAIL_USER}>`,
      to: email,
      subject: '🔑 Tu código de acceso — CertificadoYa',
      text: `Tu código de acceso es: ${codigo}\n\nExpira en 10 minutos.`,
      html: `
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
          <div style="text-align:center;background:#547c24;color:white;padding:1.5rem;border-radius:12px 12px 0 0">
            <h2 style="margin:0;font-size:1.3rem">🔑 Acceso al blog</h2>
          </div>
          <div style="background:white;padding:2rem;border:1px solid #e8ece6;border-radius:0 0 12px 12px">
            <p style="margin:0 0 1rem;color:#2d3a1f">Tu código de acceso es:</p>
            <div style="background:#f3f9eb;padding:1.2rem;text-align:center;border-radius:10px;margin-bottom:1rem">
              <span style="font-size:2rem;font-weight:800;color:#547c24;letter-spacing:6px">${codigo}</span>
            </div>
            <p style="color:#9aab8a;font-size:.8rem">Expira en 10 minutos.</p>
          </div>
        </div>
      `,
    })
    return true
  } catch {
    return false
  }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  const url = new URL(req.url)
  const action = url.searchParams.get('action') || ''

  const supabase = createClient(supabaseUrl, supabaseKey)

  try {
    // ── ENVIAR LOGIN (OTP) ──
    if (action === 'enviar-login' && req.method === 'POST') {
      const { email } = await req.json()
      if (!email) {
        return new Response(JSON.stringify({ error: 'Email requerido' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      const codigo = String(Math.floor(100000 + Math.random() * 900000))
      const expira = new Date(Date.now() + 10 * 60 * 1000).toISOString()

      // Upsert lector
      await supabase.from('blog_lectores').upsert({
        email,
        token: codigo,
        token_expira: expira,
        ultimo_acceso: new Date().toISOString(),
      }, { onConflict: 'email' })

      const sent = await sendOtp(email, codigo)
      return new Response(JSON.stringify({ success: true, enviado: sent }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // ── VERIFICAR LOGIN (OTP) ──
    if (action === 'verificar-login' && req.method === 'POST') {
      const { email, codigo } = await req.json()
      if (!email || !codigo) {
        return new Response(JSON.stringify({ error: 'Email y código requeridos' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      const { data: lector } = await supabase
        .from('blog_lectores')
        .select('id, email, nombre, token, token_expira')
        .eq('email', email)
        .maybeSingle()

      if (!lector) {
        return new Response(JSON.stringify({ error: 'Email no registrado' }), { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      if (lector.token !== codigo) {
        return new Response(JSON.stringify({ error: 'Código incorrecto' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      if (new Date(lector.token_expira) < new Date()) {
        return new Response(JSON.stringify({ error: 'Código expirado. Solicita uno nuevo.' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      // Limpiar token y actualizar acceso
      await supabase.from('blog_lectores').update({
        token: '',
        ultimo_acceso: new Date().toISOString(),
      }).eq('email', email)

      return new Response(JSON.stringify({
        success: true,
        user: { email: lector.email, nombre: lector.nombre },
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // ── ENVIAR PREGUNTA ──
    if (action === 'preguntar' && req.method === 'POST') {
      const { email, user_name, pregunta, articulo_slug } = await req.json()
      if (!email || !pregunta || !articulo_slug) {
        return new Response(JSON.stringify({ error: 'Faltan campos requeridos' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      // Verificar que el email existe como lector
      const { data: lector } = await supabase
        .from('blog_lectores')
        .select('id')
        .eq('email', email)
        .maybeSingle()

      if (!lector) {
        return new Response(JSON.stringify({ error: 'Debes iniciar sesión primero' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      await supabase.from('blog_preguntas').insert({
        articulo_slug,
        user_email: email,
        user_name: user_name || '',
        pregunta,
      })

      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // ── OBTENER PREGUNTAS ──
    if (action === 'preguntas' && req.method === 'GET') {
      const slug = url.searchParams.get('slug')
      if (!slug) {
        return new Response(JSON.stringify({ error: 'slug requerido' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      const { data: preguntas } = await supabase
        .from('blog_preguntas')
        .select('id, user_name, pregunta, respuesta, created_at')
        .eq('articulo_slug', slug)
        .eq('visible', true)
        .order('created_at', { ascending: false })
        .limit(50)

      return new Response(JSON.stringify({ preguntas: preguntas || [] }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // ── LISTAR TÉCNICOS (para directorio) ──
    if (action === 'listar-tecnicos' && req.method === 'GET') {
      const { data: tecnicos, error } = await supabase
        .from('tecnicos')
        .select('id, nombre, titulacion, provincia, telefono, created_at')
        .eq('verificado', true)
        .order('created_at', { ascending: false })
        .limit(200)

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }

      // Ocultar parte del teléfono por privacidad
      const sanitized = (tecnicos || []).map(t => ({
        ...t,
        telefono: t.telefono ? t.telefono.slice(0, 4) + '***' + t.telefono.slice(-3) : '',
      }))

      return new Response(JSON.stringify({ tecnicos: sanitized }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    return new Response(JSON.stringify({ error: 'Acción no válida' }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
