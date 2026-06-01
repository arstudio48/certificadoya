// Stripe Webhook Handler for CertificadoYa
// Deploy: supabase functions deploy stripe-webhook
// Set secrets: supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...
//             supabase secrets set STRIPE_SECRET_KEY=sk_live_...
//             supabase secrets set RESEND_API_KEY=re_...

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

const endpointSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET') || ''
const resendApiKey = Deno.env.get('RESEND_API_KEY') || ''

interface Lead {
  nombre_cliente: string
  telefono_cliente: string
  email_cliente: string
  codigo_postal: string
  zona: string
  m2: number | null
  tipo_inmueble: string
  presupuesto_min: number | null
  presupuesto_max: number | null
  estado: string
  fuente: string
  stripe_session_id: string
  stripe_payment_intent: string
}

// ── Email helpers ──
async function sendEmail(to: string, subject: string, text: string) {
  if (!resendApiKey) return
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendApiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'CertificadoYa <info@certificadoya.es>',
        to,
        subject,
        html: `<div style="font-family: 'Montserrat', sans-serif; max-width: 560px; margin: 0 auto; padding: 20px;"><p style="color: #3d4f2e; line-height: 1.6;">${text.replace(/\n/g, '<br>')}</p></div>`
      })
    })
  } catch (_) { /* email no crítico */ }
}

async function sendAdminEmail(subject: string, text: string) {
  if (!resendApiKey) return
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendApiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'CertificadoYa <info@certificadoya.es>',
        to: 'artbriher@gmail.com',
        subject,
        html: `<div style="font-family: sans-serif; max-width: 560px; margin: 0 auto; padding: 20px;"><p style="color: #333; line-height: 1.6;">${text.replace(/\n/g, '<br>')}</p></div>`
      })
    })
  } catch (_) { /* email no crítico */ }
}

serve(async (req) => {
  try {
    // ── Verify webhook signature ──
    const signature = req.headers.get('stripe-signature')
    if (!signature) {
      console.error('Missing stripe-signature header')
      return new Response('Missing stripe-signature header', { status: 400 })
    }

    const body = await req.text()
    let event: Stripe.Event

    try {
      event = stripe.webhooks.constructEvent(body, signature, endpointSecret)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Invalid signature'
      console.error('Webhook signature verification failed:', message)
      return new Response(`Webhook Error: ${message}`, { status: 400 })
    }

    console.log(`Received event: ${event.type} [id: ${event.id}]`)

    // ── Handle checkout.session.completed ──
    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session

      if (session.payment_status !== 'paid') {
        console.log(`Session ${session.id} payment_status = ${session.payment_status}, skipping`)
        return new Response('Event received (not paid yet)', { status: 200 })
      }

      const meta = session.metadata || {}

      const lead: Lead = {
        nombre_cliente: meta.name || 'Stripe Payment',
        telefono_cliente: meta.phone || '',
        email_cliente: meta.email || '',
        codigo_postal: meta.cp || '',
        zona: meta.city || '',
        m2: meta.m2 ? parseInt(meta.m2) : null,
        tipo_inmueble: meta.tipo || '',
        presupuesto_min: meta.price ? parseInt(meta.price) : null,
        presupuesto_max: meta.price ? parseInt(meta.price) : null,
        estado: 'pagado',
        fuente: 'stripe',
        stripe_session_id: session.id,
        stripe_payment_intent: typeof session.payment_intent === 'string' ? session.payment_intent : ''
      }

      const { error: insertError } = await supabase.from('leads').insert([lead])
      if (insertError) {
        console.error('Error saving lead from webhook:', insertError)
        // Don't return error to Stripe — Stripe would retry and cause duplicates.
        // Log and acknowledge instead.
      } else {
        console.log(`Lead saved from session ${session.id}`)
      }

      // ── Send confirmation email ──
      if (resendApiKey && meta.email) {
        try {
          await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${resendApiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              from: 'CertificadoYa <info@certificadoya.es>',
              to: meta.email,
              subject: '✅ Pago confirmado — CertificadoYa',
              html: `
                <div style="font-family: 'Montserrat', sans-serif; max-width: 560px; margin: 0 auto; padding: 20px;">
                  <div style="text-align: center; margin-bottom: 24px;">
                    <div style="display: inline-block; background: #edf4e5; border-radius: 50%; width: 64px; height: 64px; line-height: 64px; font-size: 28px;">✅</div>
                  </div>
                  <h1 style="color: #2d3a1f; font-size: 1.3rem; text-align: center; margin-bottom: 8px;">¡Pago confirmado!</h1>
                  <p style="color: #6b7b5e; text-align: center; font-size: 0.9rem; margin-bottom: 24px;">
                    Gracias <strong>${meta.name || ''}</strong>, tu pago se ha procesado correctamente.
                  </p>
                  <div style="background: #f7f9f6; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <p style="margin: 0 0 8px; color: #3d4f2e; font-size: 0.85rem;"><strong>Resumen de tu pedido:</strong></p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📍 Zona: ${meta.city || ''}</p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">📐 Superficie: ${meta.m2 || ''} m² (${meta.tipo || ''})</p>
                    <p style="margin: 4px 0; color: #6b7b5e; font-size: 0.82rem;">💰 Importe: ${meta.price || ''}€</p>
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
        } catch (_) { /* email no crítico */ }
      }

      // ── Send notification to admin ──
      if (resendApiKey) {
        try {
          await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${resendApiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              from: 'CertificadoYa <info@certificadoya.es>',
              to: 'artbriher@gmail.com',
              subject: `🟢 Nuevo pago recibido (webhook) — ${meta.name || ''} — ${meta.city || ''}`,
              html: `
                <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
                  <h2 style="color: #547c24;">🟢 Nuevo pago recibido</h2>
                  <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Cliente</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.name || ''}</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Email</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.email || ''}</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Teléfono</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.phone || ''}</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Zona</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.city || ''} (CP: ${meta.cp || ''})</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Inmueble</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.m2 || ''} m² - ${meta.tipo || ''}</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Importe</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${meta.price || ''}€</td></tr>
                    <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">Session ID</td><td style="padding: 8px; border-bottom: 1px solid #eee; font-size: 0.82rem;">${session.id}</td></tr>
                  </table>
                  <p style="color: #666; font-size: 14px; margin-top: 16px;">
                    Este pago fue procesado desde el webhook de Stripe. Asigna un técnico desde el panel de administración.
                  </p>
                </div>
              `
            })
          })
        } catch (_) { /* email no crítico */ }
      }

      // ── Handle credit purchase (técnico compra créditos) ──
      if (meta.tipo === 'compra_creditos' && meta.tecnico_id) {
        const cantidadCredits = parseInt(meta.cantidad_creditos || '0')
        if (cantidadCredits > 0) {
          // Update técnico saldo
          const { data: currentTec } = await supabase
            .from('tecnicos')
            .select('saldo_creditos, nombre, email')
            .eq('id', meta.tecnico_id)
            .single()

          if (currentTec) {
            await supabase
              .from('tecnicos')
              .update({ saldo_creditos: (currentTec.saldo_creditos || 0) + cantidadCredits })
              .eq('id', meta.tecnico_id)

            // Insert transaction record
            await supabase
              .from('transacciones_tecnicos')
              .insert({
                tecnico_id: meta.tecnico_id,
                tipo: 'compra_creditos',
                cantidad: cantidadCredits,
                importe_eur: parseFloat(meta.importe_total || '0'),
                concepto: `Compra de ${cantidadCredits} créditos`,
                stripe_payment_intent: typeof session.payment_intent === 'string' ? session.payment_intent : '',
                stripe_session_id: session.id
              })

            // Send confirmation to técnico
            if (currentTec.email) {
              await sendEmail(currentTec.email,
                `✅ ${cantidadCredits} créditos añadidos — CertificadoYa`,
                `Se han añadido ${cantidadCredits} créditos a tu cuenta. Saldo actual: ${(currentTec.saldo_creditos || 0) + cantidadCredits} créditos.`)
            }

            // Notify admin
            await sendAdminEmail(`💰 Compra de créditos — ${currentTec.nombre || 'Técnico'}`,
              `Técnico compró ${cantidadCredits} créditos por ${meta.importe_total || '?'}€`)
          }
        }
      }

      // ── Handle premium subscription ──
      if (meta.tipo === 'suscripcion_premium' && meta.tecnico_id) {
        const subscriptionId = typeof session.subscription === 'string' ? session.subscription : ''
        const customerId = typeof session.customer === 'string' ? session.customer : ''

        await supabase
          .from('tecnicos')
          .update({
            modelo_pago: 'premium',
            stripe_customer_id: customerId,
            stripe_subscription_id: subscriptionId,
            premium_hasta: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
          })
          .eq('id', meta.tecnico_id)

        // Insert transaction
        await supabase
          .from('transacciones_tecnicos')
          .insert({
            tecnico_id: meta.tecnico_id,
            tipo: 'suscripcion_premium',
            cantidad: 0,
            importe_eur: parseFloat(meta.importe_premium || '49.99'),
            concepto: 'Suscripción premium mensual',
            stripe_session_id: session.id,
            stripe_payment_intent: typeof session.payment_intent === 'string' ? session.payment_intent : ''
          })

        // Get técnico email
        const { data: tec } = await supabase.from('tecnicos').select('nombre, email').eq('id', meta.tecnico_id).single()
        if (tec?.email) {
          await sendEmail(tec.email,
            `🌟 Suscripción Premium activa — CertificadoYa`,
            `¡Tu suscripción premium ya está activa! Disfruta de leads ilimitados sin coste adicional.`)
        }
      }
    }

    // ── Handle customer.subscription.updated ──
    if (event.type === 'customer.subscription.updated') {
      const subscription = event.data.object as Stripe.Subscription

      // ── Update técnico premium status by subscription_id ──
      const { data: tec } = await supabase
        .from('tecnicos')
        .select('id, nombre, email')
        .eq('stripe_subscription_id', subscription.id)
        .maybeSingle()

      if (tec) {
        if (subscription.status === 'active' || subscription.status === 'trialing') {
          // Actualizar premium_hasta al final del período actual
          await supabase
            .from('tecnicos')
            .update({
              modelo_pago: 'premium',
              premium_hasta: new Date((subscription.current_period_end || 0) * 1000).toISOString(),
              updated_at: new Date().toISOString()
            })
            .eq('id', tec.id)

          if (tec.email) {
            await sendEmail(tec.email,
              `🔄 Suscripción renovada — CertificadoYa`,
              `Tu suscripción premium se ha renovado hasta el ${new Date((subscription.current_period_end || 0) * 1000).toLocaleDateString('es-ES')}.`)
          }
        } else if (subscription.status === 'past_due' || subscription.status === 'canceled' || subscription.status === 'unpaid' || subscription.status === 'incomplete_expired') {
          await supabase
            .from('tecnicos')
            .update({
              modelo_pago: 'lead',
              premium_hasta: null,
              updated_at: new Date().toISOString()
            })
            .eq('id', tec.id)

          if (tec.email) {
            await sendEmail(tec.email,
              `⚠️ Suscripción premium finalizada — CertificadoYa`,
              `Tu suscripción premium ha finalizado. A partir de ahora se te cobrará por lead. Recarga créditos para seguir aceptando encargos.`)
          }
        }
      }

      // ── Existing lead update logic ──
      const customerEmail = typeof subscription.customer === 'string'
        ? subscription.customer
        : (subscription.customer as Stripe.Customer | null)?.email || ''

      console.log(`Subscription updated: ${subscription.id}, status: ${subscription.status}`)

      const meta = subscription.metadata || {}
      if (meta.lead_id) {
        const { error: updateError } = await supabase
          .from('leads')
          .update({
            estado: subscription.status === 'active' ? 'pagado' : 'cancelado',
            updated_at: new Date().toISOString()
          })
          .eq('id', meta.lead_id)

        if (updateError) {
          console.error(`Error updating lead ${meta.lead_id}:`, updateError)
        } else {
          console.log(`Lead ${meta.lead_id} updated to status: ${subscription.status}`)
        }
      }

      // Also try to find the lead by customer email
      if (customerEmail && !meta.lead_id) {
        const { data: existingLeads } = await supabase
          .from('leads')
          .select('id')
          .eq('email_cliente', customerEmail)
          .order('created_at', { ascending: false })
          .limit(1)

        if (existingLeads && existingLeads.length > 0) {
          const { error: updateError } = await supabase
            .from('leads')
            .update({
              estado: subscription.status === 'active' ? 'pagado' : 'cancelado',
              updated_at: new Date().toISOString()
            })
            .eq('id', existingLeads[0].id)

          if (updateError) {
            console.error(`Error updating lead ${existingLeads[0].id}:`, updateError)
          } else {
            console.log(`Lead ${existingLeads[0].id} updated via email match to: ${subscription.status}`)
          }
        }
      }
    }

    // ── Handle invoice.payment_succeeded (renew premium) ──
    if (event.type === 'invoice.payment_succeeded') {
      const invoice = event.data.object as Stripe.Invoice
      if (invoice.subscription) {
        const subId = typeof invoice.subscription === 'string' ? invoice.subscription : ''
        const { data: tec } = await supabase
          .from('tecnicos')
          .select('id')
          .eq('stripe_subscription_id', subId)
          .maybeSingle()

        if (tec) {
          // Extender premium_hasta 30 días más desde ahora
          await supabase
            .from('tecnicos')
            .update({
              premium_hasta: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
              modelo_pago: 'premium'
            })
            .eq('id', tec.id)

          // Register renewal transaction
          const amount = invoice.amount_paid ? invoice.amount_paid / 100 : 49.99
          await supabase
            .from('transacciones_tecnicos')
            .insert({
              tecnico_id: tec.id,
              tipo: 'suscripcion_premium',
              cantidad: 0,
              importe_eur: amount,
              concepto: 'Renovación suscripción premium',
              stripe_payment_intent: typeof invoice.payment_intent === 'string' ? invoice.payment_intent : ''
            })
        }
      }
    }

    // ── Respond 200 OK to acknowledge the event ──
    return new Response(JSON.stringify({ received: true, type: event.type }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error'
    console.error('Unhandled error in webhook handler:', message)
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
})
