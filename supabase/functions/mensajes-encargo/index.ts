import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-admin-key, x-tecnico-token',
}

async function sendEmail(to: string, subject: string, html: string): Promise<boolean> {
  if (!RESEND_API_KEY) return false
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ from: 'CertificadoYa <info@certificadoya.es>', to, subject, html }),
    })
    return res.ok
  } catch { return false }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  const supabase = createClient(supabaseUrl, supabaseKey)

  try {
    const url = new URL(req.url)
    const encargoId = url.searchParams.get('encargo_id')
    const token = req.headers.get('x-tecnico-token') || ''

    // ─── GET: Listar mensajes de un encargo ───
    if (req.method === 'GET') {
      if (!encargoId) {
        return new Response(JSON.stringify({ error: 'encargo_id requerido' }), {
          status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Verificar acceso: token de técnico o admin
      if (token) {
        const { data: tecnico } = await supabase
          .from('tecnicos')
          .select('id')
          .eq('token', token)
          .eq('activo', true)
          .single()
        if (!tecnico) {
          return new Response(JSON.stringify({ error: 'Token inválido' }), {
            status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          })
        }
      } else {
        // Sin token, permitir solo lectura pública del último mensaje (para preview)
        // O denegar
      }

      const { data, error } = await supabase
        .from('mensajes_encargo')
        .select('*')
        .eq('encargo_id', encargoId)
        .order('created_at', { ascending: true })

      if (error) throw error

      return new Response(JSON.stringify({ success: true, mensajes: data || [] }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ─── POST: Enviar mensaje ───
    if (req.method === 'POST') {
      const { encargo_id, mensaje, de_tecnico } = await req.json()

      if (!encargo_id || !mensaje) {
        return new Response(JSON.stringify({ error: 'encargo_id y mensaje requeridos' }), {
          status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // Verificar token si es mensaje de técnico
      if (de_tecnico !== false) {
        if (!token) {
          return new Response(JSON.stringify({ error: 'Token requerido para mensajes de técnico' }), {
            status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          })
        }
        const { data: tecnico } = await supabase
          .from('tecnicos')
          .select('id, nombre')
          .eq('token', token)
          .eq('activo', true)
          .single()
        if (!tecnico) {
          return new Response(JSON.stringify({ error: 'Token inválido' }), {
            status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          })
        }
      }

      // Insertar mensaje
      const { data: msg, error: insertError } = await supabase
        .from('mensajes_encargo')
        .insert({
          encargo_id,
          de_tecnico: de_tecnico !== false,
          mensaje,
          leido: false,
        })
        .select('id, encargo_id, de_tecnico, created_at')
        .single()

      if (insertError) throw insertError

      // Notificar por email
      if (de_tecnico !== false) {
        // Técnico escribió → notificar al cliente
        const { data: lead } = await supabase
          .from('leads')
          .select('nombre_cliente, email, id')
          .eq('id', encargo_id)
          .single()

        if (lead?.email) {
          await sendEmail(
            lead.email,
            '💬 Nuevo mensaje de tu técnico — CertificadoYa',
            `<div style="font-family:Outfit,sans-serif;max-width:500px;margin:0 auto;background:#f5f7f2;padding:20px;border-radius:12px">
              <h2 style="color:#1a1a1a;margin:0 0 12px">💬 Nuevo mensaje</h2>
              <p style="color:#6b7b5e;line-height:1.5">Tu técnico te ha escrito. Responde desde el enlace:</p>
              <div style="background:#eef4e8;padding:12px;border-radius:8px;margin:16px 0;font-style:italic;color:#3d5e1a">${mensaje}</div>
              <a href="https://www.certificadoya.es/chat.html?encargo=${lead.id}" style="display:inline-block;background:#547c24;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600">Responder</a>
            </div>`
          )
        }
      } else {
        // Cliente escribió → notificar al técnico
        const { data: lead } = await supabase
          .from('leads')
          .select('nombre_cliente, tecnico_id, id')
          .eq('id', encargo_id)
          .single()

        if (lead?.tecnico_id) {
          const { data: tecnico } = await supabase
            .from('tecnicos')
            .select('email, nombre')
            .eq('id', lead.tecnico_id)
            .single()

          if (tecnico?.email) {
            await sendEmail(
              tecnico.email,
              `💬 ${lead.nombre_cliente || 'Un cliente'} te ha escrito — CertificadoYa`,
              `<div style="font-family:Outfit,sans-serif;max-width:500px;margin:0 auto;background:#f5f7f2;padding:20px;border-radius:12px">
                <h2 style="color:#1a1a1a;margin:0 0 12px">💬 Nuevo mensaje</h2>
                <p style="color:#6b7b5e;line-height:1.5"><strong>${lead.nombre_cliente || 'Cliente'}</strong> ha respondido a tu mensaje.</p>
                <div style="background:#eef4e8;padding:12px;border-radius:8px;margin:16px 0;font-style:italic;color:#3d5e1a">${mensaje}</div>
                <p style="color:#6b7b5e;font-size:14px">Entra al panel para ver el historial completo.</p>
              </div>`
            )
          }
        }
      }

      return new Response(JSON.stringify({ success: true, mensaje: msg }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
