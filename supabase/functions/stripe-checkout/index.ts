import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import Stripe from 'https://esm.sh/stripe@13.10.0?target=deno'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') || '', {
  apiVersion: '2023-10-16',
  httpClient: Stripe.createFetchHttpClient()
})

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const url = new URL(req.url)
  const action = url.searchParams.get('action')

  // ============================================================
  // ACTION: create — Crear sesión de pago Stripe
  // ============================================================
  if (action === 'create' || !action) {
    try {
      const { price, service, city, name, email, phone, description, m2, tipo, cp } = await req.json()

      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [{
          price_data: {
            currency: 'eur',
            product_data: {
              name: service,
              description: description || `Certificado en ${city}`
            },
            unit_amount: Math.round(price * 100)
          },
          quantity: 1
        }],
        mode: 'payment',
        success_url: 'https://certificadoya.es/success.html?session_id={CHECKOUT_SESSION_ID}',
        cancel_url: 'https://certificadoya.es/',
        metadata: {
          service, city, name, email, phone,
          m2: String(m2 || ''),
          tipo: tipo || '',
          cp: cp || '',
          price: String(price)
        }
      })

      return new Response(JSON.stringify({
        url: session.url,
        sessionId: session.id
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error('Error creating checkout session:', error)
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  // ============================================================
  // ACTION: confirm — Verificar pago y guardar lead + enviar email
  // ============================================================
  if (action === 'confirm') {
    try {
      const { session_id } = await req.json()
      if (!session_id) {
        return new Response(JSON.stringify({ error: 'Missing session_id' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const session = await stripe.checkout.sessions.retrieve(session_id)
      if (session.payment_status !== 'paid') {
        return new Response(JSON.stringify({ error: 'Payment not completed', status: session.payment_status }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const meta = session.metadata || {}

      // Guardar lead en Supabase
      const lead = {
        nombre_cliente: meta.name || 'Stripe Payment',
        telefono_cliente: meta.phone || '',
        email_cliente: meta.email || '',
        codigo_postal: meta.cp || '',
        zona: meta.city || '',
        m2: meta.m2 ? parseInt(meta.m2) : null,
        tipo_inmueble: meta.tipo || '',
        presupuesto_min: meta.price ? parseInt(meta.price) : null,
        presupuesto_max: meta.price ? parseInt(meta.price) : null,
        estado: 'nuevo',
        fuente: 'stripe'
      }

      const { error } = await supabase.from('leads').insert([lead])
      if (error) {
        console.error('Error saving lead:', error)
        return new Response(JSON.stringify({ error: 'Error saving lead' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      // ── Enviar email de confirmación al cliente ──
      const emailCliente = meta.email || ''
      const nombreCliente = meta.name || ''
      const ciudad = meta.city || ''
      const precio = meta.price || ''
      const m2Str = meta.m2 || ''
      const tipoStr = meta.tipo || ''

      try {
        if (emailCliente) {
          await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${RESEND_API_KEY}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              from: 'CertificadoYa <info@certificadoya.es>',
              to: emailCliente,
              subject: '✅ Pago confirmado — CertificadoYa',
              html: `
                <div style="font-family: 'Montserrat', sans-serif; max-width: 560px; margin: 0 auto; padding: 20px;">
                  <div style="text-align: center; margin-bottom: 24px;">
                    <div style="display: inline-block; background: #edf4e5; border-radius: 50%; width: 64px; height: 64px; line-height: 64px; font-size: 28px;">✅</div>
                  </div>
                  <h1 style="color: #2d3a1f; font-size: 1.3rem; text-align: center; margin-bottom: 8px;">¡Pago confirmado!</h1>
                  <p style="color: #6b7b5e; text-align: center; font-size: 0.9rem; margin-bottom: 24px;">
                    Gracias <strong>${nombreCliente}</strong>, tu pago se ha procesado correctamente.
                  </p>
                  <div style="background: #f7f9f6; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <p style="margin: 0 0 8px; color: #3d4f2e; font-size: 0.85rem;"><strong>Resumen de tu pedido:</strong></p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📍 Zona: ${ciudad}</p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📐 Superficie: ${m2Str} m² (${tipoStr})</p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">💰 Importe: ${precio}€</p>
                  </div>
                  <p style="color: #6b7b5e; font-size: 0.88rem; line-height: 1.6;">
                    <strong>¿Qué pasa ahora?</strong><br>
                    1. Hemos asignado tu solicitud a un técnico de tu zona.<br>
                    2. El técnico te contactará al teléfono que indicaste <strong>en menos de 24 horas</strong>.<br>
                    3. Acordaréis una visita para realizar el certificado.<br><br>
                    Si tienes cualquier duda, responde a este email o llámanos.
                  </p>
                  <hr style="border: none; border-top: 1px solid #e8ece6; margin: 24px 0;">
                  <p style="color: #9aab8a; font-size: 0.78rem; text-align: center;">
                    CertificadoYa · certificadoya.es
                  </p>
                </div>
              `
            })
          })
        }
      } catch (_) { /* email no crítico */ }

      // ── Enviar notificación a CertificadoYa ──
      try {
        await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: 'CertificadoYa <info@certificadoya.es>',
            to: 'artbriher@gmail.com',
            subject: `🟢 Nuevo pago recibido — ${nombreCliente} — ${ciudad}`,
            html: `
              <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
                <h2 style="color: #547c24;">🟢 Nuevo pago recibido</h2>
                <table style="width: 100%; border-collapse: collapse;">
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Cliente</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${nombreCliente}</td></tr>
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${emailCliente}</td></tr>
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.phone || ''}</td></tr>
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Zona</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${ciudad} (CP: ${meta.cp || ''})</td></tr>
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${m2Str} m² - ${tipoStr}</td></tr>
                  <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Importe</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${precio}€</td></tr>
                </table>
                <p style="color: #666; font-size: 14px; margin-top: 16px;">
                  Asigna un técnico y confirma el servicio desde el panel de administración.
                </p>
              </div>
            `
          })
        })
      } catch (_) { /* email no crítico */ }

      return new Response(JSON.stringify({ success: true, lead }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } catch (error) {
      console.error('Error confirming payment:', error)
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  }

  return new Response(JSON.stringify({ error: 'Unknown action' }), {
    status: 400,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
})
