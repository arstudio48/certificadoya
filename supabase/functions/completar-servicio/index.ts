// Edge Function: completar-servicio
// Técnico marca un lead como completado → cambia estado + email reseña
// Deploy: supabase functions deploy completar-servicio --no-verify-jwt
// Secrets needed: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { lead_id, tecnico_id, token } = await req.json()

    if (!lead_id || !tecnico_id || !token) {
      return new Response(JSON.stringify({ error: 'Faltan datos' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Verificar que el técnico es el asignado
    const { data: lead, error: leadError } = await supabase
      .from('leads')
      .select('id, nombre_cliente, email_cliente, zona, m2, tipo_inmueble, presupuesto_min, presupuesto_max, tecnico_asignado')
      .eq('id', lead_id)
      .eq('tecnico_asignado', tecnico_id)
      .single()

    if (leadError || !lead) {
      return new Response(JSON.stringify({ error: 'Lead no encontrado o no asignado a este técnico' }), {
        status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Cambiar estado a completado
    const { error: updateError } = await supabase
      .from('leads')
      .update({ estado: 'completado', completado_at: new Date().toISOString() })
      .eq('id', lead_id)

    if (updateError) {
      return new Response(JSON.stringify({ error: 'Error al actualizar lead' }), {
        status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Enviar email de reseña al cliente
    const emailCliente = lead.email_cliente || ''
    const nombreCliente = lead.nombre_cliente || ''

    if (emailCliente && RESEND_API_KEY) {
      try {
        await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: 'CertificadoYa <info@certificadoya.es>',
            to: emailCliente,
            subject: '¿Qué tal fue tu experiencia? ⭐',
            html: `
              <div style="font-family: 'DM Sans', sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
                <div style="text-align:center;font-size:2.5rem;margin-bottom:16px">⭐</div>
                <h1 style="color:#1a2e1e;font-size:1.3rem;text-align:center;margin-bottom:8px">¡Certificado entregado!</h1>
                <p style="color:#6b7b5e;text-align:center;font-size:.9rem;margin-bottom:20px">
                  Hola ${nombreCliente}, esperamos que el servicio haya sido de tu agrado.
                </p>
                <div style="background:#f0faf2;border-radius:12px;padding:20px;text-align:center;margin-bottom:20px">
                  <p style="color:#1a2e1e;font-size:.95rem;margin-bottom:12px"><strong>¿Nos recomendarías?</strong></p>
                  <p style="color:#6b7b5e;font-size:.82rem;line-height:1.5">
                    Tu opinión nos ayuda a mejorar y a que otros propietarios confíen en nosotros.<br>
                    Solo te llevará 30 segundos.
                  </p>
                  <a href="https://www.certificadoya.es/resena?lead=${lead_id}" 
                     style="display:inline-block;background:#16a34a;color:#fff;padding:.7rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;margin-top:12px">
                    Dejar reseña ⭐
                  </a>
                </div>
                <p style="color:#b0c0a8;font-size:.78rem;text-align:center;margin-top:20px">
                  CertificadoYa · certificadoya.es
                </p>
              </div>
            `
          })
        })
      } catch (_) { /* email no crítico */ }
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
