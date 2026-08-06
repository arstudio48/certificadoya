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
    const { lead_id, tecnico_id, token, registro_cee, pdf_url } = await req.json()

    if (!lead_id || !tecnico_id || !token) {
      return new Response(JSON.stringify({ error: 'Faltan datos' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ⚠️ ANTI-ELUSIÓN (Capa 2): sin evidencia de entrega (nº de registro CEE o PDF),
    // el servicio NO se cierra ni se paga al técnico. El 82% queda retenido en CertificadoYa
    // hasta que el técnico aporte prueba de que emitió y registró el certificado.
    if (!registro_cee && !pdf_url) {
      return new Response(JSON.stringify({
        error: 'Debes adjuntar el nº de registro del CEE o el PDF del certificado para cobrar. El pago se libera tras verificar la entrega.',
        requiere_evidencia: true
      }), {
        status: 422, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
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

    // Guardar evidencia y dejar en pendiente_verificacion (NO pagar aún).
    // El payout (82% al técnico, 18% para ti) solo se libera tras que CertificadoYa
    // verifique el registro del CEE. El técnico no cobra hasta entregar prueba real.
    const { error: updateError } = await supabase
      .from('leads')
      .update({
        estado: 'pendiente_verificacion',
        registro_cee: registro_cee || null,
        pdf_certificado_url: pdf_url || null,
        completado_at: new Date().toISOString()
      })
      .eq('id', lead_id)

    if (updateError) {
      return new Response(JSON.stringify({ error: 'Error al actualizar lead' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    // Notificar a CertificadoYa para verificar el registro antes de liberar el pago.
    try {
      await fetch(`${supabaseUrl}/functions/v1/notificar-lead`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${supabaseServiceKey}` },
        body: JSON.stringify({
          nombre_cliente: lead.nombre_cliente,
          email_cliente: lead.email_cliente,
          telefono_cliente: '',
          provincia: lead.zona,
          tipo_inmueble: lead.tipo_inmueble,
          m2: lead.m2,
          presupuesto_min: lead.presupuesto_min,
          presupuesto_max: lead.presupuesto_max,
          fuente: 'verificacion_pendiente',
          estado: 'pendiente_verificacion',
          nota: `Técnico ${tecnico_id} entregó evidencia (registro: ${registro_cee || 'n/a'}, pdf: ${pdf_url ? 'sí' : 'no'}). Verificar y liberar pago.`
        })
      })
    } catch (_) { /* no crítico */ }

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
                  <a href="https://www.certificadooya.es/resena?lead=${lead_id}"
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

    return new Response(JSON.stringify({ success: true, estado: 'pendiente_verificacion', mensaje: 'Evidencia recibida. El pago se libera tras verificar el registro del CEE.' }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
