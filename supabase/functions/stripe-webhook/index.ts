// Stripe Webhook Handler for CertificadoYa
// Flujo: aceptar-presupuesto → Stripe Checkout → este webhook
// Deploy: supabase functions deploy stripe-webhook
// Secrets: STRIPE_WEBHOOK_SECRET, STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

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

    // ================================================================
    // Handle checkout.session.completed
    // ================================================================
    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session
      const meta = session.metadata || {}

      if (meta.tipo === 'pago_presupuesto' && meta.presupuesto_id) {
        // ── Nuevo flujo: pago de presupuesto por un lead existente ──
        const presupuestoId = meta.presupuesto_id
        const paymentIntent = typeof session.payment_intent === 'string' ? session.payment_intent : ''

        console.log(`Pago recibido para presupuesto ${presupuestoId}, payment_intent: ${paymentIntent}`)

        // Actualizar presupuesto a pagado
        const { error: presupuestoError } = await supabase
          .from('presupuestos')
          .update({
            estado: 'pagado',
            stripe_payment_intent: paymentIntent,
            fecha_pago: new Date().toISOString()
          })
          .eq('id', presupuestoId)

        if (presupuestoError) {
          console.error(`Error actualizando presupuesto ${presupuestoId}:`, presupuestoError)
        } else {
          console.log(`Presupuesto ${presupuestoId} marcado como pagado`)
        }

        // Actualizar lead asociado
        if (meta.lead_id) {
          const { error: leadError } = await supabase
            .from('leads')
            .update({ estado: 'pagado' })
            .eq('id', meta.lead_id)

          if (leadError) {
            console.error(`Error actualizando lead ${meta.lead_id}:`, leadError)
          } else {
            console.log(`Lead ${meta.lead_id} marcado como pagado`)
          }
        }

        // ── Notificación al admin vía email cron ──
        // El script email_notifier.py ya revisa periódicamente leads nuevos/pagados
        // y envía notificaciones por Gmail SMTP

        return new Response(JSON.stringify({
          received: true,
          type: event.type,
          presupuesto_id: presupuestoId,
          action: 'presupuesto_pagado'
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        })
      }

      // ── Flujo antiguo (sin presupuesto_id) — solo log ──
      console.log(`Session ${session.id} completed sin presupuesto_id en metadata, ignorando`)
    }

    // ================================================================
    // Handle customer.subscription.updated
    // ================================================================
    if (event.type === 'customer.subscription.updated') {
      const subscription = event.data.object as Stripe.Subscription
      const customerEmail = typeof subscription.customer === 'string'
        ? subscription.customer
        : (subscription.customer as Stripe.Customer | null)?.email || ''

      console.log(`Subscription updated: ${subscription.id}, status: ${subscription.status}`)

      const meta = subscription.metadata || {}

      if (meta.lead_id) {
        const { error: updateError } = await supabase
          .from('leads')
          .update({ estado: subscription.status === 'active' ? 'pagado' : 'cancelado' })
          .eq('id', meta.lead_id)

        if (updateError) {
          console.error(`Error updating lead ${meta.lead_id}:`, updateError)
        } else {
          console.log(`Lead ${meta.lead_id} updated to: ${subscription.status}`)
        }
      }

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
            .update({ estado: subscription.status === 'active' ? 'pagado' : 'cancelado' })
            .eq('id', existingLeads[0].id)

          if (updateError) {
            console.error(`Error updating lead ${existingLeads[0].id}:`, updateError)
          } else {
            console.log(`Lead ${existingLeads[0].id} updated via email match to: ${subscription.status}`)
          }
        }
      }
    }

    // ── Respond 200 OK for all events ──
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
