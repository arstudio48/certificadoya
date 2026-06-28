import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const ADMIN_SECRET_KEY = Deno.env.get('ADMIN_SECRET_KEY') || ''
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-admin-key',
}

// ─── Verificar clave de admin ───
function isAdmin(req: Request): boolean {
  const key = req.headers.get('x-admin-key') || ''
  return key === ADMIN_SECRET_KEY
}

// ─── Enviar email con Resend ───
async function sendEmail(to: string, subject: string, html: string): Promise<boolean> {
  if (!RESEND_API_KEY) return false
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'CertificadoYa <info@certificadoya.es>',
        to,
        subject,
        html,
      }),
    })
    return res.ok
  } catch {
    return false
  }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Verificar autenticación
  if (!isAdmin(req)) {
    return new Response(JSON.stringify({ error: 'No autorizado' }), {
      status: 401,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }

  const supabase = createClient(supabaseUrl, supabaseKey)

  try {
    // ─── GET: Listar técnicos ───
    if (req.method === 'GET') {
      const url = new URL(req.url)
      const filtro = url.searchParams.get('filtro') || 'todos'

      let query = supabase
        .from('tecnicos')
        .select('*')
        .order('created_at', { ascending: false })

      if (filtro === 'pendientes') {
        query = query.is('verificado', false).eq('activo', true)
      } else if (filtro === 'activos') {
        query = query.eq('verificado', true).eq('activo', true)
      } else if (filtro === 'rechazados') {
        query = query.eq('activo', false)
      }

      const { data, error } = await query

      if (error) throw error

      return new Response(JSON.stringify({ success: true, tecnicos: data || [] }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // ─── POST: Aprobar / Rechazar ───
    if (req.method === 'POST') {
      const { action, tecnicoId } = await req.json()

      if (!action || !tecnicoId) {
        return new Response(JSON.stringify({ error: 'Faltan datos (action, tecnicoId)' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      if (action === 'aprobar') {
        const { data: tecnico, error: findError } = await supabase
          .from('tecnicos')
          .select('id, nombre, email')
          .eq('id', tecnicoId)
          .single()

        if (findError || !tecnico) {
          return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        const { error: updateError } = await supabase
          .from('tecnicos')
          .update({ verificado: true, activo: true, updated_at: new Date().toISOString() })
          .eq('id', tecnicoId)

        if (updateError) throw updateError

        // Email de aprobación
        await sendEmail(
          tecnico.email,
          `✅ ¡Bienvenido a la red de técnicos, ${tecnico.nombre}!`,
          `
            <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
              <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                <div style="background:linear-gradient(135deg,#547c24,#3d5e1a);padding:30px 40px;text-align:center">
                  <div style="font-size:28px;font-weight:700;color:#fff">✅ Validación completada</div>
                </div>
                <div style="padding:35px 40px">
                  <h1 style="font-size:22px;font-weight:700;color:#1a1a1a;margin:0 0 10px 0">¡Tu perfil ha sido validado!</h1>
                  <p style="font-size:15px;color:#6b7b5e;line-height:1.5;margin:0 0 20px">Hola <strong>${tecnico.nombre}</strong>, estamos encantados de darte la bienvenida.</p>
                  <div style="text-align:center;margin:25px 0">
                    <a href="https://www.certificadoya.es/pool-encargos.html" style="display:inline-block;background:#547c24;color:#fff;text-decoration:none;padding:14px 32px;border-radius:8px;font-weight:600;font-size:16px">
                      Acceder al panel →
                    </a>
                  </div>
                </div>
                <div style="padding:20px 40px;text-align:center;font-size:12px;color:#9aab8a;border-top:1px solid #eef4e8">
                  <p style="margin:0">CertificadoYa.es</p>
                </div>
              </div>
            </div>
          `
        )

        return new Response(JSON.stringify({ success: true, message: 'Técnico aprobado' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      if (action === 'rechazar') {
        const { data: tecnico, error: findError } = await supabase
          .from('tecnicos')
          .select('id, nombre, email')
          .eq('id', tecnicoId)
          .single()

        if (findError || !tecnico) {
          return new Response(JSON.stringify({ error: 'Técnico no encontrado' }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        const { error: updateError } = await supabase
          .from('tecnicos')
          .update({ activo: false, verificado: false, updated_at: new Date().toISOString() })
          .eq('id', tecnicoId)

        if (updateError) throw updateError

        await sendEmail(
          tecnico.email,
          `❌ Solicitud no aprobada — CertificadoYa`,
          `
            <div style="font-family:Outfit,'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f7f2;padding:30px 15px">
              <div style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)">
                <div style="background:linear-gradient(135deg,#6b7280,#4b5563);padding:30px 40px;text-align:center">
                  <div style="font-size:28px;font-weight:700;color:#fff">❌ Solicitud no aprobada</div>
                </div>
                <div style="padding:35px 40px">
                  <p style="font-size:15px;color:#6b7b5e;line-height:1.5;margin:0">Hola ${tecnico.nombre}, hemos revisado tu solicitud y en este momento no podemos validar tu perfil. Puedes contactarnos respondiendo a este correo si crees que ha habido un error.</p>
                </div>
              </div>
            </div>
          `
        )

        return new Response(JSON.stringify({ success: true, message: 'Técnico rechazado' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      return new Response(JSON.stringify({ error: 'Acción no válida' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
